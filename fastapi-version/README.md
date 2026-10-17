# FastAPI version of the Lab

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-plain.svg" width="70" />

This folder is an optional, alternative way to complete the "Serving Machine
Learning Models through a RESTish API" lab. You may build the lab using
Flask (`api.py` in the repository root, the default path) or FastAPI (this
folder). Both serve the same four trained artifacts, through the same four
URL paths, accepting the same request bodies and returning the same
response bodies. Pick whichever one you want to learn; you do not need to
submit both versions.

If you have not yet worked through `api.py`, read that file first. The
comments in `api_fastapi.py` assume you already understand the machine
learning side (loading the four `.joblib` artifacts once at startup,
building a one row DataFrame from the request, calling `.predict()`) and
focus only on what changes when the same API is rebuilt with FastAPI.

## Folder contents

| File                               | Purpose                                                                                                                       |
|:-----------------------------------|:------------------------------------------------------------------------------------------------------------------------------|
| `api_fastapi.py`                   | The FastAPI application. Equivalent to `api.py`.                                                                              |
| `requirements.txt`                 | Python packages for this track, in place of `requirements/base.txt` and `requirements/prod.txt`.                              |
| `api_consumer_from_dev_fastapi.py` | Calls all four endpoints against a locally running `api_fastapi.py`. Equivalent to `frontend/api_consumer_from_dev_flask.py`. |
| `Dockerfile.fastapi-uvicorn-app`   | Containerizes this API behind Gunicorn and Uvicorn. Equivalent to `dockerfiles/Dockerfile.flask-gunicorn-app`.                |
| `docker-compose-fastapi.yaml`      | A small Compose file for building and running the container on its own, for quick testing.                                    |
| `Procfile`                         | For deploying this track to Render, in place of the repository root `Procfile`.                                               |

## Running it locally (no Docker)

From the **repository root** (not from inside this folder), install the
dependencies and start the development server:

```bash
pip install -r fastapi-version/requirements.txt -c requirements/constraints.txt
```

```bash
python fastapi-version/api_fastapi.py
```

This starts a server on [http://127.0.0.1:5000](http://127.0.0.1:5000), the same address and port
`api.py` uses, so you only ever run one of the two at a time on port 5000
unless you deliberately change the port in one of them.

Running it from the repository root matters here for the same reason it
matters for `api.py`: the model files are loaded from a path built relative
to `model/`. `api_fastapi.py` resolves that path from its own file
location rather than from whichever directory you happened to launch it
from, so it will still find the model files correctly even if you `cd`
into `fastapi-version/` first and run `uvicorn api_fastapi:app --reload`
from there instead. Either way of starting it works.

Once it is running, open [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs) in a browser. This
page is generated automatically from the code and lets you send a real
request to your own server directly from the browser, with an example
value already filled in for every field. There is no equivalent page in
the Flask version.

To test it from a script instead, in a second terminal, with the server
still running:

```bash
python fastapi-version/api_consumer_from_dev_fastapi.py
```

## Running it in Docker, on its own

From the repository root:

```bash
docker compose -f fastapi-version/docker-compose-fastapi.yaml up -d --build
```

This builds the image and publishes it on `http://127.0.0.1:8001` (not
8000, so that it does not collide with the Flask track if both happen to be
built at the same time). Tear it down the same way you tear down the rest
of the lab:

```bash
docker compose -f fastapi-version/docker-compose-fastapi.yaml down -v --rmi all
```

## Putting FastAPI behind Nginx (Intermediate and Advanced tiers)

If you want FastAPI running behind the same reverse proxy setup used for
the Flask track, two small, manual edits are all that is needed. Nginx does not
need to know which framework is listening on the
other end of a proxied connection, so nothing else in
`container-volumes/nginx/nginx.conf` needs to change.

1. We add a service for this container in `docker-compose-dev.yaml`, following
   the same pattern already used for `flask-gunicorn-app`:

   ```yaml
   fastapi-uvicorn-app:
     image: servingmlmodels-fastapi-uvicorn-app:1.0.0
     build:
       context: .
       dockerfile: ./fastapi-version/Dockerfile.fastapi-uvicorn-app
     restart: always
   ```

   We also edit the `docker-compose.yaml` file by adding the following:

   ```yaml
   fastapi-uvicorn-app:
     image: servingmlmodels-fastapi-uvicorn-app:1.0.0
     expose:
      - "8000"
   ```
   The container is reachable from other containers (Nginx) on the shared
   Docker network without being published to your host machine directly;
   Nginx remains the only supported entry point, exactly as it is for the
   Flask track.

2. We change the upstream pool's in `container-volumes/nginx/nginx.conf`
   line from:

   ```nginx
   upstream flask_backend {
       server flask-gunicorn-app:8000;
   }
   ```

   to:

   ```nginx
   upstream flask_backend {
       server fastapi-uvicorn-app:8000;
   }
   ```

   (Renaming the upstream block itself, `flask_backend`, is optional; it is
   just a label, and leaving it as `flask_backend` does not change how the
   proxy behaves.)

Run from the repository root to rebuild and restart the whole stack, scaling the FastAPI container to 2 replicas and the Flask container to 0:

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  up -d \
  --build \
  --scale flask-gunicorn-app=0 \
  --scale fastapi-uvicorn-app=2
```

```bash
docker compose restart nginx
```
After rebuilding and restarting, the same `https://localhost/api/...` URLs
used throughout the lab will route to the FastAPI container instead of the
Flask one, with no change needed to the frontend HTML pages or anything else downstream of the
API.

## Running it in Render

Steps:

1. Make sure `./model/` (all four `.joblib` files) is committed to your repository -- Render builds from your Git history, so files that exist only on your own machine will not be deployed.
2. Create a `Procfile` in the `fastapi-version` directory, containing exactly:

   ```text
   web: gunicorn -k uvicorn_worker.UvicornWorker -w 4 -b 0.0.0.0:$PORT api_fastapi:app
   ```

   Render auto-detects and runs this on deploy.
3. Push your changes to GitHub.
4. Go to [https://dashboard.render.com](https://dashboard.render.com)
5. Click **+ New -> Web Service**
6. Connect your GitHub repository
7. Select the branch (`main`). Render auto-detects Python.
8. Specify the name of your service
9. Under "Build Command", use:

   ```text
   pip install -r requirements.txt -c ../requirements/constraints.txt
   ```

10. Under "Start Command", use:

   ```text
   gunicorn -k uvicorn_worker.UvicornWorker -w 4 -b 0.0.0.0:$PORT api_fastapi:app
   ```
11. Select the "Free" plan
12. Click "Deploy Web Service"
13. Copy the URL of your deployed service

## Key changes from the Flask version

Everything below is also explained in comments at the point it happens in
`api_fastapi.py`. This table is a quick reference once you have read that
file.

| Concern                                                                            | Flask (`api.py`)                                                                                                    | FastAPI (`api_fastapi.py`)                                                                                                                                 |
|:-----------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Reading the request body                                                           | `request.get_json()` returns a plain dictionary; nothing checks its shape                                           | A Pydantic model (for example `RevenueRegressionRequest`) is declared once; FastAPI parses, validates, and converts the request body into it automatically |
| A badly formed request                                                             | Reaches your function regardless; may produce a wrong prediction or a confusing error from deep inside scikit-learn | Rejected before your function runs, with HTTP 422 and a precise, structured message naming the field that was wrong                                        |
| Declaring a route                                                                  | `@app.route("/path", methods=["POST"])`                                                                             | `@app.post("/path")`                                                                                                                                       |
| Building the response                                                              | `jsonify({...})`                                                                                                    | Return a plain dictionary (or a Pydantic model); FastAPI converts it to JSON automatically                                                                 |
| Cross origin requests                                                              | `flask_cors`, `CORS(app, resources={...})`                                                                          | `fastapi.middleware.cors.CORSMiddleware`, added with `app.add_middleware(...)`                                                                             |
| Local development server                                                           | `app.run(debug=True, port=5000)`                                                                                    | `uvicorn.run("api_fastapi:app", host="127.0.0.1", port=5000, reload=True)`, or the `uvicorn api_fastapi:app --reload` command                              |
| Interactive API documentation                                                      | None built in                                                                                                       | Automatic, at `/docs` and `/redoc`, generated from the Pydantic models and type hints                                                                      |
| Production server                                                                  | `gunicorn -w 5 -b 0.0.0.0:8000 api:app`                                                                             | `gunicorn -k uvicorn_worker.UvicornWorker -w 5 -b 0.0.0.0:8000 api_fastapi:app` (see note below)                                                           |
| Route handler style                                                                | Ordinary `def` functions                                                                                            | Still ordinary `def` functions, deliberately not `async def`; see the note below                                                                           |
| Request field names that are not valid Python identifiers (`"Annual Income (k$)"`) | Not an issue; Flask never turns the request into a typed object                                                     | Handled with a Pydantic `Field(alias=...)`; see the note below                                                                                             |

### Gunicorn Layered on top of Uvicorn

FastAPI needs an ASGI server to "speak HTTP", and Uvicorn is the one used in the theory
and in this lab. Gunicorn is actually layered **on top of Uvicorn**, not instead of it: Gunicorn
remains the process manager (it starts, monitors, and restarts worker
processes, and binds the shared port), exactly the role it already plays
for the Flask track of this lab, while Uvicorn does the actual work of speaking HTTP
inside each worker process.


```bash
gunicorn -k uvicorn_worker.UvicornWorker -w 4 -b 0.0.0.0:$PORT api_fastapi:app
```

### Why the route handlers are not written as `async def`

FastAPI supports `async def` route handlers, and a lot of FastAPI material
online uses them by default, which can give the impression that this is
simply the "correct" or "modern" way to write every route. For this lab,
it is not.

Every route here does one blocking, CPU bound piece of work: calling
`.predict()` (or `.transform()`) on a scikit-learn pipeline that was loaded
into memory at startup. A plain `def` route is
automatically run by FastAPI in a worker thread, so a slow prediction does
not stop the server from handling other requests at the same time. If
these functions were written as `async def` instead, without anything
inside them actually being awaited, the blocking `.predict()` call would
run directly on FastAPI's single event loop and freeze it completely until
that one prediction finished, which would make every other request, to any
endpoint, wait in line behind it. That would quietly cancel out the exact
benefit that running several Gunicorn worker processes is meant to provide
(see the Dockerfile and the Nginx scaling notes elsewhere in this lab), so
it is worth getting right from the start rather than discovering it as a
performance problem later.

### Why the clustering endpoint needs `Field(alias=...)`

The mall customer segmentation model was trained on a DataFrame with the
column names `Age`, `Annual Income (k$)`, and `Spending Score (1-100)`.
None of those three strings can be used directly as the name of a Python
class attribute, because two of them contain spaces and one also contains
parentheses and a dollar sign. `CustomerSegmentRequest` in
`api_fastapi.py` works around this with a normal, valid attribute name for
each field (`age`, `annual_income_k`, `spending_score`), paired with
`Field(alias="...")` telling FastAPI which original key to read that value
from in the incoming JSON. The request body sent by a client is completely
unaffected by this and still uses the original column names, exactly as it
does for `api.py`.
