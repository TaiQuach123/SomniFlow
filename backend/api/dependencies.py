from fastapi import Request, HTTPException


def get_checkpointer(request: Request):
    checkpointer = getattr(request.app.state, "checkpointer", None)
    if not checkpointer:
        raise HTTPException(status_code=500, detail="Checkpointer not initialized")
    return checkpointer


def get_graph(request: Request):
    graph = getattr(request.app.state, "graph", None)
    if not graph:
        raise HTTPException(status_code=500, detail="Graph not initialized")
    return graph


def get_pool(request: Request):
    pool = getattr(request.app.state, "pool", None)
    if not pool:
        raise HTTPException(status_code=500, detail="Pool not initialized")
    return pool
