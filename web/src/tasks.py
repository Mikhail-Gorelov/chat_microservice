from src.celery import app


@app.task(name="main.tasks.add", queue="blog", exchange="celery")
def add(x, y):
    raise NotImplementedError()


@app.task(name="main.tasks.mul", queue="blog", exchange="celery")
def mul(x, y):
    raise NotImplementedError()


@app.task(name="main.tasks.xsum", queue="blog", exchange="celery")
def xsum(numbers):
    raise NotImplementedError()
