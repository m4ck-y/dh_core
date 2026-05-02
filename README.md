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
