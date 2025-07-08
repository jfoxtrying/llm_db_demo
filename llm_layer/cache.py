import functools, hashlib, json, sqlite3, pathlib

CACHE_PATH = pathlib.Path(__file__).parent / "llm_cache.db"
# create table once (own short-lived conn, so no thread issue)
with sqlite3.connect(CACHE_PATH) as _db:
    _db.execute("CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT)")

def cached(func):
    @functools.wraps(func)
    def wrapper(payload):
        k = hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        # open connection just for this request → always safe in worker thread
        with sqlite3.connect(CACHE_PATH, check_same_thread=False) as db:
            row = db.execute("SELECT v FROM cache WHERE k=?", (k,)).fetchone()
            if row:
                return json.loads(row[0])
            val = func(payload)
            db.execute("INSERT OR REPLACE INTO cache VALUES (?,?)",
                       (k, json.dumps(val)))
            db.commit()
            return val
    return wrapper