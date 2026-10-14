# Roll Number: cb.sc.u4cys23021
# Name: K.C.K.SANJAI

- Base image: python:3.12-slim
- Web server: Flask (port 5000)
- Database: PostgreSQL

```bash
docker compose up -d --build
```

- Open http://localhost:5000

- username: `sanjai` and password: `sanjai235`

```bash
docker compose down -v   
```

```bash
docker image inspect mt-webauth
```