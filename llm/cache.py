import functools, hashlib, json, sqlite3, pathlib

_cache_db = sqlite3.connect(pathlib.Path(__file__).parent / "llm_cache.db")
_cache_db.execute("CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT)")

def cached(func):
    @functools.wraps(func)
    def wrapper(payload):
        k = hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        row = _cache_db.execute("SELECT v FROM cache WHERE k=?", (k,)).fetchone()
        if row:
            return json.loads(row[0])
        val = func(payload)
        _cache_db.execute("INSERT INTO cache VALUES (?,?)", (k, json.dumps(val)))
        _cache_db.commit()
        return val
    return wrapper