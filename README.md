## Instalando

### Iniciando os bancos de dados inicial e final

```bash
docker-compose up -d
```

### Criar os volumes para carregar os dados da pipeline

```bash
bash setup_volume.sh
```

### Construindo a imagem do Meltano pra ser executada

```bash
cd /src/my-first-project-meltano
```

```bash
docker build --tag meltano-demo-project:dev .
```

### Iniciando o Airflow

```bash
cd /src/airflow
```

```bash
astro dev start
```