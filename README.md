# dh_core

Microservicio maestro de personas del ecosistema Digital Hospital.

## Responsabilidad

Duene del schema `people` en PostgreSQL. Gestiona:

- **Persona**: datos personales, fecha de nacimiento, nacionalidad, genero.
- **Contacto**: emails, telefonos, direcciones.
- **Identidad**: CURP, RFC, numero de seguro social.
- **Social**: contactos de emergencia, plataformas sociales, vinculos familiares.

## Dependencias

- `dh_shared` — modelos SQLAlchemy, enums, utilidades de seguridad.
- PostgreSQL — esquemas `people` y `expedient`.

## Endpoints

Ver `ENDPOINTS.md`.

## Inter-Service

Consumido por `dh_onboarding_back` para creacion y actualizacion de personas.

## Variables de Entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `POSTGRES_URL` | `postgresql+asyncpg://...` | Conexion a base de datos |
| `SERVICE_LOGGER_TRACER_URL` | `""` | URL de VitalTrace para logging |

## Systemd Service Management

### 1. Copiar definición del servicio

```bash
sudo cp /home/m4ck-y/.me/dh/dh_core/docs/dh_core.service /etc/systemd/system/
```

O crearlo manualmente:

```bash
sudo nano /etc/systemd/system/dh_core.service
```

### 2. Gestionar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable dh_core
sudo systemctl start dh_core
sudo systemctl status dh_core
journalctl -u dh_core -f
```

## Systemd Service Management

### 1. Copiar definición del servicio

```bash
sudo cp /home/m4ck-y/.me/dh/dh_core/docs/dh_core.service /etc/systemd/system/
```

O crearlo manualmente:

```bash
sudo nano /etc/systemd/system/dh_core.service
```

### 2. Gestionar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable dh_core
sudo systemctl start dh_core
sudo systemctl status dh_core
journalctl -u dh_core -f
```
