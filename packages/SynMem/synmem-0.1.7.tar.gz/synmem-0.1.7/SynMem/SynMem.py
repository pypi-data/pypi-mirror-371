﻿
import os
from pathlib import Path
import sqlite3
import threading
from datetime import datetime, timedelta
from rapidfuzz import fuzz, process
import numpy as np
import shutil
import time
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class SynMem:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SynMem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.dbLock = threading.Lock()
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.sessionStart = datetime.now()
        self.sensoryLimit       = 10
        self.sensoryExpireUnit  = "days"
        self.sensoryExpireValue = 7
        self.memoryExpireUnit   = "minutes"
        self.memoryExpireValue  = 30
        self.imageExpireUnit    = "days"
        self.imageExpireValue   = 30
        self.cleanupExpireUnit  = "days"
        self.cleanupExpireValue = 15
        self.perceptionLimit    = 10
        self.perception         = []
        self.senDir = None
        self.stmUserConversationDetails = None
        self.stmUserInteractionDetails  = None
        self.ltmUserConversationDetails = None
        self.ltmUserInteractionDetails  = None
        self.stmCreatedImages = None
        self.ltmCreatedImages = None
        self.stmCreatedImageDetails = None
        self.ltmCreatedImageDetails = None
        self.embeddingModel = None

    def setSynMemDirs(self, dirs):
        """
        Set internal directory attributes for SynMem storage.

        You can provide either a dictionary or a list/tuple:

        - **If using a dict:** Keys are attribute names (see below). Order does not matter.
        - **If using a list or tuple:** Values are assigned by position, following the order below.

        Supported attribute names (keys, in order for lists/tuples):
            - 'senDir'
            - 'stmUserConversationDetails'
            - 'stmUserInteractionDetails'
            - 'ltmUserConversationDetails'
            - 'ltmUserInteractionDetails'
            - 'stmCreatedImages'
            - 'ltmCreatedImages'
            - 'stmCreatedImageDetails'
            - 'ltmCreatedImageDetails'

        Any omitted values (missing keys or too-short lists) are set to None.

        Parameters
        ----------
        dirs : dict or list/tuple
            Either:
            - dict: Maps attribute names to directory paths.
            - list/tuple: Directory paths in the order above.

        Examples
        --------
        # Using a dictionary (recommended)
        synmem.setSynMemDirs({
            'senDir': '/path/to/sensory',
            'stmCreatedImages': '/path/to/stm/images',
            # others can be omitted, defaulting to None
        })

        # Using a list (must match the order above)
        synmem.setSynMemDirs([
            '/path/to/sensory',
            '/path/to/stm/convo',
            '/path/to/stm/interact',
            # ... etc., in order ...
        ])
        """
        attrNames = [
            'senDir',
            'stmUserConversationDetails', 'stmUserInteractionDetails',
            'ltmUserConversationDetails', 'ltmUserInteractionDetails',
            'stmCreatedImages', 'ltmCreatedImages',
            'stmCreatedImageDetails', 'ltmCreatedImageDetails'
        ]
        if isinstance(dirs, dict):
            for attr in attrNames:
                setattr(self, attr, dirs.get(attr))
        else:
            for attr, value in zip(attrNames, dirs + [None] * (len(attrNames) - len(dirs))):
                setattr(self, attr, value)

    def setSynMemConfig(self, config):
        """
        Set runtime configuration values for SynMem memory and expiration behavior.

        You can provide either a dictionary (recommended) or a list/tuple of values in the order shown below.

        Supported configuration parameters (with defaults):
            - 'perceptionLimit'    (default: 10)
            - 'sensoryLimit'       (default: 10)
            - 'sensoryExpireUnit'  (default: "days")
            - 'sensoryExpireValue' (default: 7)
            - 'memoryExpireUnit'   (default: "minutes")
            - 'memoryExpireValue'  (default: 30)
            - 'imageExpireUnit'    (default: "days")
            - 'imageExpireValue'   (default: 30)
            - 'cleanupExpireUnit'  (default: "days")
            - 'cleanupExpireValue' (default: 15)

        Any omitted values use the default above.

        Parameters
        ----------
        config : dict or list/tuple
            Either:
            - dict: Maps configuration parameter names to values.
            - list/tuple: Values in the order above.

        Examples
        --------
        # Using a dictionary (recommended)
        synmem.setSynMemConfig({
            'perceptionLimit': 20,
            'memoryExpireValue': 60
        })

        # Using a list (order: perceptionLimit, sensoryLimit, ...)
        synmem.setSynMemConfig([20, 10, "days", 7, "minutes", 60, "days", 30, "days", 15])
        """
        attrDefaults = [
            ('perceptionLimit',    10),
            ('sensoryLimit',       10),
            ('sensoryExpireUnit',  "days"),
            ('sensoryExpireValue', 7),
            ('memoryExpireUnit',   "minutes"),
            ('memoryExpireValue',  30),
            ('imageExpireUnit',    "days"),
            ('imageExpireValue',   30),
            ('cleanupExpireUnit',  "days"),
            ('cleanupExpireValue', 15),
        ]
        if isinstance(config, dict):
            for attr, default in attrDefaults:
                setattr(self, attr, config.get(attr, default))
        else:
            for idx, (attr, default) in enumerate(attrDefaults):
                setattr(self, attr, config[idx] if idx < len(config) else default)

    def setSynMemModel(self, model):
        self.embeddingModel = model

    def getSynMemModel(self):
        return self.embeddingModel

    def getTimedelta(self, unit, value):
        return timedelta(**{unit: value})

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def ensureDir(self, path):
        dirName = os.path.dirname(path)
        if dirName and not os.path.exists(dirName):
            os.makedirs(dirName, exist_ok=True)

    # ─── Database ────────────────────────────────────────────────────────
    def createDatabase(self, path, tableSchema):
        self.ensureDir(path)
        if not os.path.exists(path):
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute(tableSchema)
                conn.commit()

    def createPersonalDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    def createMemoryDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    def createDetailsDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    # ─── Save ────────────────────────────────────────────────────────
    def savePerception(self, ctx: str):
        if len(self.perception) >= self.perceptionLimit:
            self.perception.pop(0)
        self.perception.append(ctx)

    def saveData(self, path, ctx, response=None):
        self.ensureDir(path)
        timestamp = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )
        try:
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(memory)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'response' in columns:
                    cursor.execute(
                        'INSERT INTO memory (dtStamp, content, response) VALUES (?, ?, ?)',
                        (timestamp, contentText, response)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO memory (dtStamp, content) VALUES (?, ?)',
                        (timestamp, contentText)
                    )
                conn.commit()
            return
        except sqlite3.OperationalError:
            logger.error(f"OperationalError while saving data:", exc_info=True)
        except Exception:
            logger.error(f"Unexpected error while saving data:", exc_info=True)

    def saveSensory(self, ctx, response, user, path):
        self.ensureDir(path)
        self.createPersonalDatabase(self.getDir(path, f"{user}.db"))
        db = self.getDir(path, f"{user}.db")
        self.ensureDir(db)
        with self.dbLock, sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM memory')
            count = cursor.fetchone()[0]
            if count >= self.sensoryLimit:
                cursor.execute('DELETE FROM memory WHERE id = (SELECT MIN(id) FROM memory)')
                conn.commit()
        self.saveData(db, ctx, response)

    def saveConversationDetails(self, ctx, response, user, path):
        db = self.getDir(path, "STM.db")
        self.ensureDir(db)
        timestamp = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )
        self.createMemoryDatabase(db)
        try:
            with self.dbLock, sqlite3.connect(db) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO memory (user, dtStamp, content, response) VALUES (?, ?, ?, ?)",
                    (user, timestamp, contentText, response)
                )
                conn.commit()
        except Exception:
            logger.error(f"Error saving data to {db}:", exc_info=True)

    def saveInteractionDetails(self, user, path):
        db = self.getDir(path, "Details.db")
        self.ensureDir(db)
        self.createDetailsDatabase(db)
        self.saveData(db, user)

    def saveImageDetails(self, imageSubject, path):
        db = self.getDir(path, "Details.db")
        self.ensureDir(db)
        self.createDetailsDatabase(db)
        self.saveData(db, imageSubject)

    def setImageDir(self, base):
        now = datetime.now()
        return self.getDir(base, now.strftime("%Y").lower(), now.strftime("%m"), now.strftime("%d").lower())

    def getNextAvailableFilename(self, directory, baseName, extension=".png"):
        counter = 1
        while True:
            filename = f"{baseName}{counter}{extension}"
            filePath = self.getDir(directory, filename)
            if not os.path.exists(filePath):
                return filename
            counter += 1

    # def saveCreatedImage(self, imageSubject, imageData, path1, path2):
    #     image = Image.open(BytesIO(imageData.content))
    #     imageDir = self.setImageDir(path1)
    #     self.ensureDir(imageDir)
    #     filename = self.getNextAvailableFilename(imageDir, imageSubject, ".png")
    #     imagePath = self.getDir(imageDir, filename)
    #     self.ensureDir(imagePath)
    #     self.saveImageDetails(filename, path2)
    #     image.save(imagePath)
    #     image.show()
    def saveCreatedImage(self, imageSubject, imageData, path1, path2):
        # Handle both cases: PIL.Image.Image vs Response-like
        if isinstance(imageData, Image.Image):
            image = imageData
        else:
            image = Image.open(BytesIO(imageData.content))

        imageDir = self.setImageDir(path1)
        self.ensureDir(imageDir)
        filename = self.getNextAvailableFilename(imageDir, imageSubject, ".png")
        imagePath = self.getDir(imageDir, filename)
        self.ensureDir(imagePath)

        self.saveImageDetails(filename, path2)

        image.save(imagePath)
        image.show()


    # ─── Retrieve ────────────────────────────────────────────────────────
    def recallMemory(self, query: str, paths: list, user: str = None, type: str = 'Embedded', topK=5, minScore: int = 60, showProgress: bool = False):
        type = type.lower()
        if type in ('embedding', 'embedded'):
            return self.recallEmbeddedMemory(query, paths, user, topK, showProgress)
        elif type == 'rapid':
            return self.recallRapidMemory(query, paths, user, topK, minScore)
        else:
            raise ValueError(f"Unknown recall type: {type}, expected 'embedded' or 'rapid'.")

    def recallEmbeddedMemory(self, query: str, paths: list, user: str = None, topK=5, showProgress: bool = False, minScore: int = 60):
        model = self.embeddingModel
        if model is None:
            logger.error("Embedding model not set. Falling back to Rapid recall. Use synmem.setEmbeddingModel(model).", exc_info=True)
            return self.recallRapidMemory(query, paths, user, topK, minScore)

        rows = []
        for path in paths:
            dbFiles = []
            if os.path.isdir(path):
                dbFiles = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.db')]
            elif os.path.isfile(path):
                dbFiles = [path]
            else:
                continue

            for dbFile in dbFiles:
                try:
                    with sqlite3.connect(dbFile) as conn:
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA table_info(memory)")
                        cols = [col[1] for col in cursor.fetchall()]
                    # Always select all 4 fields. If the DB doesn't have user, pad it below.
                    if 'user' in cols:
                        if user:
                            query_str = "SELECT user, dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE"
                            params = [user]
                        else:
                            query_str = "SELECT user, dtStamp, content, response FROM memory"
                            params = []
                    else:
                        query_str = "SELECT '', dtStamp, content, response FROM memory"
                        params = []
                    db_rows = self.retrieveMemoryFromDb(dbFile, query_str, params)
                    for row in db_rows:
                        if len(row) == 4:
                            rows.append(row)
                        elif len(row) == 3:
                            rows.append(('', *row))
                except Exception as ex:
                    logger.error(f"Error reading for semantic search: {dbFile}: {ex}", exc_info=True)
                    continue

        if not rows:
            return []

        contents = [content for (_, _, content, _) in rows]
        entry_embeddings = model.encode(contents, show_progress_bar=showProgress)
        query_embedding = model.encode([query], show_progress_bar=showProgress)[0]

        scores = np.dot(entry_embeddings, query_embedding) / (
            np.linalg.norm(entry_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        top_indices = np.argsort(scores)[::-1][:topK]
        results = [rows[i] for i in top_indices]
        return results

    def recallRapidMemory(self, query: str, paths: list, user: str = None, topK=5, minScore: int = 60):
        rows = []
        for path in paths:
            dbFiles = []
            if os.path.isdir(path):
                dbFiles = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.db')]
            elif os.path.isfile(path):
                dbFiles = [path]
            else:
                continue

            for dbFile in dbFiles:
                try:
                    with sqlite3.connect(dbFile) as conn:
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA table_info(memory)")
                        cols = [col[1] for col in cursor.fetchall()]
                    if 'user' in cols:
                        if user:
                            query_str = "SELECT user, dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE"
                            params = [user]
                        else:
                            query_str = "SELECT user, dtStamp, content, response FROM memory"
                            params = []
                    else:
                        query_str = "SELECT '', dtStamp, content, response FROM memory"
                        params = []
                    db_rows = self.retrieveMemoryFromDb(dbFile, query_str, params)
                    for row in db_rows:
                        if len(row) == 4:
                            rows.append(row)
                        elif len(row) == 3:
                            rows.append(('', *row))
                except Exception as ex:
                    logger.error(f"Error reading for fuzzy search: {dbFile}: {ex}", exc_info=True)
                    continue

        if not rows:
            return []

        contents = [content for (_, _, content, _) in rows]
        resultsWithScores = process.extract(query, contents, scorer=fuzz.token_sort_ratio, limit=topK)
        results = [
            rows[idx]
            for (content, score, idx) in resultsWithScores if score >= minScore
        ]
        return results



    # def recallEmbeddedMemory(self, query: str, paths: list, user: str = None, topK=5, showProgress: bool = False, minScore: int = 60):
    #     model = self.embeddingModel
    #     if model is None:
    #         logger.error("Embedding model not set. Falling back to Rapid recall. Use synmem.setEmbeddingModel(model).", exc_info=True)
    #         return self.recallRapidMemory(query, paths, user, topK, minScore)

    #     rows = []
    #     for path in paths:
    #         dbFiles = []
    #         if os.path.isdir(path):
    #             dbFiles = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.db')]
    #         elif os.path.isfile(path):
    #             dbFiles = [path]
    #         else:
    #             continue

    #         for dbFile in dbFiles:
    #             try:
    #                 with sqlite3.connect(dbFile) as conn:
    #                     cursor = conn.cursor()
    #                     cursor.execute("PRAGMA table_info(memory)")
    #                     cols = [col[1] for col in cursor.fetchall()]
    #                 if 'user' in cols and user:
    #                     query_str = "SELECT dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE"
    #                     params = [user]
    #                 else:
    #                     query_str = "SELECT dtStamp, content, response FROM memory"
    #                     params = []
    #                 db_rows = self.retrieveMemoryFromDb(dbFile, query_str, params)
    #                 for row in db_rows:
    #                     # row[0]=dtStamp, row[1]=content, row[2]=response
    #                     rows.append((row[0], row[1], row[2] if len(row) > 2 else ""))
    #             except Exception as ex:
    #                 #print(f"Error reading for semantic search: {dbFile}: {ex}")
    #                 logger.error(f"Error reading for semantic search: {dbFile}: {ex}", exc_info=True)
    #                 continue

    #     if not rows:
    #         return []

    #     contents = [content for (_, content, _) in rows]
    #     entry_embeddings = model.encode(contents, show_progress_bar=showProgress)
    #     query_embedding = model.encode([query], show_progress_bar=showProgress)[0]

    #     scores = np.dot(entry_embeddings, query_embedding) / (
    #         np.linalg.norm(entry_embeddings, axis=1) * np.linalg.norm(query_embedding)
    #     )
    #     top_indices = np.argsort(scores)[::-1][:topK]
    #     results = [(rows[i][0], rows[i][1], rows[i][2]) for i in top_indices]
    #     return results

    # def recallRapidMemory(self, query: str, paths: list, user: str = None, topK=5, minScore: int = 60):
    #     """
    #     Fuzzy string matching version of recallMemory, using Rapidfuzz.
    #     Returns topK best-matching (dtStamp, content, response) entries.
    #     """
    #     rows = []
    #     for path in paths:
    #         dbFiles = []
    #         if os.path.isdir(path):
    #             dbFiles = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.db')]
    #         elif os.path.isfile(path):
    #             dbFiles = [path]
    #         else:
    #             continue

    #         for dbFile in dbFiles:
    #             try:
    #                 with sqlite3.connect(dbFile) as conn:
    #                     cursor = conn.cursor()
    #                     cursor.execute("PRAGMA table_info(memory)")
    #                     cols = [col[1] for col in cursor.fetchall()]
    #                 if 'user' in cols and user:
    #                     query_str = "SELECT dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE"
    #                     params = [user]
    #                 else:
    #                     query_str = "SELECT dtStamp, content, response FROM memory"
    #                     params = []
    #                 db_rows = self.retrieveMemoryFromDb(dbFile, query_str, params)
    #                 for row in db_rows:
    #                     rows.append((row[0], row[1], row[2] if len(row) > 2 else ""))
    #             except Exception as ex:
    #                 #print(f"Error reading for fuzzy search: {dbFile}: {ex}")
    #                 logger.error(f"Error reading for fuzzy search: {dbFile}: {ex}", exc_info=True)
    #                 continue

    #     if not rows:
    #         return []

    #     # Fuzzy match: use Rapidfuzz's process.extract, returns [(match, score, idx), ...]
    #     # We'll just score vs content field
    #     contents = [content for (_, content, _) in rows]
    #     resultsWithScores = process.extract(query, contents, scorer=fuzz.token_sort_ratio, limit=topK)
    #     # resultsWithScores = [(content, score, index), ...]
    #     results = [
    #         (rows[idx][0], rows[idx][1], rows[idx][2])
    #         for (content, score, idx) in resultsWithScores if score >= minScore
    #     ]
    #     return results

    def retrievePerception(self):
        if self.perception:
            perception = "\n".join(self.perception)
            return perception
        else:
            return "No Perception Feedback Available."

    def retrieveMemoryFromDb(self, dbFile, query, params, returnTimestampOnly=False):
        memory = []
        if os.path.exists(dbFile):
            try:
                with self.dbLock, sqlite3.connect(dbFile) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    if rows:
                        for row in rows:
                            if isinstance(row, tuple) and len(row) > 0:
                                if returnTimestampOnly:
                                    memory.append(row[1] if len(row) == 4 else row[0])  # Timestamp is always 2nd in 4-tuple or 1st in 3-tuple
                                else:
                                    # Always return (user, dtStamp, content, response)
                                    if len(row) == 4:
                                        memory.append(row)
                                    elif len(row) == 3:
                                        memory.append(('', *row))
                                    else:
                                        logger.warning(f"Skipping invalid row format in {dbFile}: {row}")
                        return memory
            except sqlite3.OperationalError:
                logger.error(f"OperationalError while retrieving data from {dbFile}:", exc_info=True)
            except Exception:
                logger.error(f"Unexpected error while retrieving data from {dbFile}:", exc_info=True)
        return memory


    # def retrieveMemoryFromDb(self, dbFile, query, params, returnTimestampOnly=False):
    #     memory = []
    #     if os.path.exists(dbFile):
    #         try:
    #             with self.dbLock, sqlite3.connect(dbFile) as conn:
    #                 cursor = conn.cursor()
    #                 cursor.execute(query, params)
    #                 rows = cursor.fetchall()
    #                 if rows:
    #                     for row in rows:
    #                         if isinstance(row, tuple) and len(row) > 0:
    #                             if returnTimestampOnly:
    #                                 memory.append(row[0])
    #                             else:
    #                                 timestamp = row[0]
    #                                 rawContent = row[1]
    #                                 response = row[2] if len(row) > 2 else ""
    #                                 decodedContent = rawContent if isinstance(rawContent, str) else str(rawContent)
    #                                 memory.append((timestamp, decodedContent, response))
    #                         else:
    #                             logger.warning(f"Skipping invalid row format in {dbFile}: {row}")
    #                 return memory
    #         except sqlite3.OperationalError:
    #             logger.error(f"OperationalError while retrieving data from {dbFile}:", exc_info=True)
    #         except Exception:
    #             logger.error(f"Unexpected error while retrieving data from {dbFile}:", exc_info=True)
    #     return memory

    def retrieveDetailsFromDb(self, dbFile, query, params):
        memory = []
        if os.path.exists(dbFile):
            with self.dbLock, sqlite3.connect(dbFile) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    timestamp = row[0]
                    contentText = row[1] if isinstance(row[1], str) else str(row[1])
                    memory.append((timestamp, contentText))
        return memory

    def retrieveSensory(self, path):
        query  = 'SELECT dtStamp, content, response FROM memory'
        params = []
        return self.retrieveMemoryFromDb(path, query, params)

    def retrieveConversationDetails(self, user, paths: list, startDate=None, endDate=None):
        dbNames = ["STM.db", "LTM.db"]
        dbs = [self.getDir(path, dbName) for path, dbName in zip(paths, dbNames)]
        query = 'SELECT dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE'
        params = [user]
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveMemoryFromDb(db, query, params)
        return memory

    def retrieveInteractionDetails(self, paths: list, startDate=None, endDate=None):
        dbs = [self.getDir(path, "Details.db") for path in paths]
        query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveDetailsFromDb(db, query, params)
        return memory

    def retrieveLastInteractionTime(self, user, paths: list):
        dbConfigs = [
            (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for i, path in enumerate(paths[:len(dbConfigs)]):
            dbName, query, params = dbConfigs[i]
            dbPath = self.getDir(path, dbName)
            timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
            if timestamps:
                try:
                    return datetime.now() - datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return datetime.now() - self.sessionStart

    def retrieveLastInteractionDate(self, user, paths: list):
        dbConfigs = [
            (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for i, path in enumerate(paths[:len(dbConfigs)]):
            dbName, query, params = dbConfigs[i]
            dbPath = self.getDir(path, dbName)
            timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
            if timestamps:
                try:
                    return datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return self.sessionStart

    def retrieveImageDetails(self, paths: list, startDate=None, endDate=None):
        dbs = [self.getDir(path, "Details.db") for path in paths]
        query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveDetailsFromDb(db, query, params)
        return memory

    def retrieveCreatedImage(self, directory, imageName):
        imagePath = self.getImageDir(directory, f"{imageName}.png")
        if os.path.exists(imagePath):
            with Image.open(imagePath) as img:
                img.show()
            return imagePath
        else:
            logger.warning(f"Image not found: {imagePath}")
            return f"Image not found: {imagePath}"

    def getImageDir(self, base, date):
        return self.getDir(base, date.strftime("%Y").lower(), date.strftime("%m"), date.strftime("%d").lower())

    def formatIsoDate(self, dateStr):
        if not dateStr:
            return None
        inputFormats = [
            "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
            "%m-%d-%y", "%d-%m-%y", "%m/%d/%y", "%d/%m/%y",
            "%m-%d-%Y %I:%M %p", "%d-%m-%Y %I:%M %p",
            "%m/%d/%Y %I:%M %p", "%d/%m/%Y %I:%M %p",
            "%Y-%m-%d %I:%M %p",
            "%I:%M %p",
            "%H:%M"
        ]
        today = datetime.today()
        try:
            dt = datetime.fromisoformat(dateStr)
        except ValueError:
            dt = self._parseKnownFormats(dateStr, inputFormats, today)
        isoDate = dt.isoformat(timespec="seconds")
        return isoDate if "T" in dateStr else f"{isoDate.split('T')[0]}T00:00:00"

    def _parseKnownFormats(self, dateStr, formats, today):
        for fmt in formats:
            try:
                dt = datetime.strptime(dateStr, fmt)
                if fmt in ("%I:%M %p", "%H:%M"):
                    dt = today.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
                return dt
            except ValueError:
                continue
        raise ValueError(
            f"Invalid date format: {dateStr}. Expected ISO format YYYY-MM-DD or formats like MM-DD-YYYY, DD-MM-YYYY, MM/DD/YYYY, DD/MM/YYYY, or even just time (e.g., 6:30 PM)."
        )

    # ─── Checks ────────────────────────────────────────────────────────
    def startAutoMaintenance(self, interval=5*60):
        def loop():
            while True:
                self._performMaintenanceChecks()
                time.sleep(interval)
        threading.Thread(target=loop, daemon=True).start()

    def performStartupChecks(self, delay: int = 1):
        checks = [
            lambda: self.removeOldSensory(self.sensoryExpireUnit, self.sensoryExpireValue),
            #lambda: self.archiveCreatedImages(self.imageExpireUnit, self.imageExpireValue),
        ]
        for check in checks:
            check()
            time.sleep(delay)

    def _performMaintenanceChecks(self, delay: int = 1):
        checks = [
            lambda: self.archiveConversationDetails(self.memoryExpireUnit, self.memoryExpireValue),
            lambda: self.archiveInteractionDetails(self.memoryExpireUnit, self.memoryExpireValue),
            lambda: self.archiveImageDetails(self.memoryExpireUnit, self.memoryExpireValue),
        ]
        for check in checks:
            check()
            time.sleep(delay)

    # ─── Maintenance ────────────────────────────────────────────────────────
    def checkDatabases(self, sourceDir, timeCheckFunc, actionFunc, expireDelta):
        if not sourceDir or not os.path.exists(sourceDir):
            return
        for root, _, files in os.walk(sourceDir, topdown=False):
            for file in files:
                try:
                    dbFile = self.getDir(root, file)
                    fileTime = timeCheckFunc(dbFile)
                    if datetime.now() - fileTime > expireDelta:
                        actionFunc(dbFile, file)
                except Exception:
                    logger.error(f"Error processing {file}:", exc_info=True)

    def moveDatabase(self, srcFile, destFile, createQuery, selectQuery, insertQuery):
        os.makedirs(os.path.dirname(destFile), exist_ok=True)
        with self.dbLock, sqlite3.connect(destFile) as destConn:
            destCursor = destConn.cursor()
            destCursor.execute(createQuery)
            destConn.commit()
        try:
            with self.dbLock, sqlite3.connect(srcFile) as srcConn:
                srcCursor = srcConn.cursor()
                srcCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory'")
                if not srcCursor.fetchone():
                    logger.warning(f"Skipping '{srcFile}' - no memory table.")
                    return
                srcCursor.execute(selectQuery)
                rows = srcCursor.fetchall()
                with sqlite3.connect(destFile) as destConn:
                    destCursor = destConn.cursor()
                    destCursor.executemany(insertQuery, rows)
                    destConn.commit()
                srcCursor.execute("PRAGMA table_info(memory)")
                columns = [col[1] for col in srcCursor.fetchall()]
                hasUser = "user" in columns
                if hasUser:
                    srcCursor.executemany(
                        "DELETE FROM memory WHERE user = ? AND dtStamp = ?",
                        [(row[0], row[1]) for row in rows]
                    )
                else:
                    srcCursor.executemany(
                        "DELETE FROM memory WHERE dtStamp = ?",
                        [(row[0],) for row in rows]
                    )
        except sqlite3.OperationalError:
            logger.error(f"OperationalError moving '{srcFile}':", exc_info=True)
        except Exception:
            logger.error(f"Unexpected error moving '{srcFile}':", exc_info=True)

    # ========== Expiration Actions ==========

    def removeOldSensory(self, expireUnit, expireValue):
        self.checkDatabases(
            self.senDir,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldInteractionDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.stmUserInteractionDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldImageDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.stmCreatedImageDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldConversationDetails(self, expireUnit, expireValue):
        path = self.getDir(self.stmDir, "STM.db")
        if not path or not os.path.exists(path):
            return
        expireThreshold = datetime.now() - self.getTimedelta(expireUnit, expireValue)
        if not os.path.exists(path):
            return
        try:
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM memory WHERE dtStamp <= ?",
                    (expireThreshold.isoformat(),)
                )
                conn.commit()
        except Exception:
            logger.error(f"Failed to remove old STM records:", exc_info=True)

    # ========== Archive Actions ==========

    def archiveConversationDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.stmUserConversationDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveConversationDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveInteractionDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.stmUserInteractionDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveInteractionDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveImageDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.stmCreatedImageDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveImageDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveCreatedImages(self, expireUnit, expireValue):
        expireDelta = self.getTimedelta(expireUnit, expireValue)
        if not self.stmCreatedImages or not os.path.exists(self.stmCreatedImages):
            return
        for root, _, files in os.walk(self.stmCreatedImages, topdown=False):
            for file in files:
                try:
                    if not file.lower().endswith(".png"):
                        continue
                    filePath = self.getDir(root, file)
                    fileTime = datetime.fromtimestamp(os.path.getmtime(filePath))
                    if datetime.now() - fileTime > expireDelta:
                        relativePath = os.path.relpath(filePath, self.stmCreatedImages)
                        destPath = self.getDir(self.ltmCreatedImages, relativePath)
                        os.makedirs(os.path.dirname(destPath), exist_ok=True)
                        shutil.move(filePath, destPath)
                except Exception:
                    logger.error(f"MemoryMaintenance Error archiving image '{file}':", exc_info=True)

    # ========== Move Helpers ==========

    def moveConversationDetails(self, dbFile, fileName):
        # If the per‐user STM DB doesn’t exist, nothing to do
        if not os.path.exists(dbFile):
            return

        # Path to your LTM aggregate DB
        ltmPath = self.getDir(self.ltmUserConversationDetails, "LTM.db")

        # Select the actual `user` column rather than inferring it from the filename
        selectQuery = '''
            SELECT user, dtStamp, content, response
            FROM memory
        '''

        # Pre‐check: make sure the table exists and has rows
        try:
            with self.dbLock, sqlite3.connect(dbFile) as srcConn:
                srcCursor = srcConn.cursor()
                srcCursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='memory'"
                )
                if not srcCursor.fetchone():
                    return

                srcCursor.execute(selectQuery)
                rows = srcCursor.fetchall()
                if not rows:
                    return
        except Exception:
            logger.error(f"Error pre-checking '{dbFile}':", exc_info=True)
            return

        # Ensure the LTM DB exists with the proper schema…
        self.createMemoryDatabase(ltmPath)

        # …then move all rows, preserving the real `user` field
        self.moveDatabase(
            srcFile=dbFile,
            destFile=ltmPath,
            createQuery='''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    dtStamp TEXT,
                    content TEXT,
                    response TEXT
                )
            ''',
            selectQuery=selectQuery,
            insertQuery='''
                INSERT INTO memory (user, dtStamp, content, response)
                VALUES (?, ?, ?, ?)
            '''
        )

    def moveInteractionDetails(self, dbFile, fileName):
        self.createDetailsDatabase(dbFile)
        ltmPath = self.getDir(self.ltmUserInteractionDetails, fileName)
        self.moveDatabase(
            dbFile,
            ltmPath,
            '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
            'SELECT dtStamp, content FROM memory',
            'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
        )

    def moveImageDetails(self, dbFile, fileName):
        self.createDetailsDatabase(dbFile)
        ltmPath = self.getDir(self.ltmCreatedImageDetails, fileName)
        self.moveDatabase(
            dbFile,
            ltmPath,
            '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
            'SELECT dtStamp, content FROM memory',
            'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
        )

    # ─── Clear ────────────────────────────────────────────────────────
    def clearPerception(self):
        self.perception.clear()

    def clearFirstEntry(self, user):
        self._clearEntryByQuery(user, 'MIN')

    def clearLastEntry(self, user):
        self._clearEntryByQuery(user, 'MAX')

    def clearAllEntries(self, user):
        senDb = self.getDir(self.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.ltmUserConversationDetails, "LTM.db")
        self._deleteByQuery(senDb, "DELETE FROM memory")
        self._deleteByQuery(stmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])
        self._deleteByQuery(ltmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])

    def _clearEntryByQuery(self, user, which):
        senDb = self.getDir(self.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.ltmUserConversationDetails, "LTM.db")
        self._deleteByQuery(
            senDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory)"
        )
        self._deleteByQuery(
            stmDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ? COLLATE NOCASE) AND user = ? COLLATE NOCASE",
            [user, user]
        )
        self._deleteByQuery(
            ltmDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ? COLLATE NOCASE) AND user = ? COLLATE NOCASE",
            [user, user]
        )

    def _deleteByQuery(self, path, query, params=None):
        if os.path.exists(path):
            try:
                with self.dbLock, sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or [])
                    conn.commit()
            except Exception:
                logger.error(f"Failed to clear from {path}:", exc_info=True)

    # ─── View ────────────────────────────────────────────────────────
    def viewDatabase(self, path, limit=None):
        return self._viewTable(path, "memory", limit)

    def viewDetailsDatabase(self, path, limit=None):
        return self._viewTable(path, "memory", limit)

    def _viewTable(self, path, tableName, limit=None):
        dbPath = path
        # If path is a directory, find a .db file inside
        if os.path.isdir(path):
            dbFiles = [f for f in os.listdir(path) if f.endswith('.db')]
            if not dbFiles:
                logger.warning(f"No .db files found in directory: {path}")
                return []
            dbPath = os.path.join(path, dbFiles[0])  # You could also loop or let the user pick
        elif not os.path.isfile(path):
            logger.warning(f"Database not found: {path}")
            return []
        try:
            with self.dbLock, sqlite3.connect(dbPath) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
                if not cursor.fetchone():
                    logger.warning(f"No '{tableName}' table in: {dbPath}")
                    return []
                cursor.execute(f"PRAGMA table_info({tableName})")
                columns = [col[1] for col in cursor.fetchall()]
                query = f"SELECT * FROM {tableName}"
                if limit:
                    query += f" ORDER BY id DESC LIMIT {limit}"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception:
            logger.error(f"[Viewer] Error reading {dbPath}:", exc_info=True)
            return []
