-- ─────────────────────────────────────────────────────────────────────────────
-- 1) DDL: CREACIÓN DE TABLAS
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE ciudad (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE instalacion (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  id_ciudad INT NOT NULL
    REFERENCES ciudad(id) ON DELETE RESTRICT,
  UNIQUE(nombre,id_ciudad)
);

CREATE TABLE deporte (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE usuario (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
  estado VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE usuario_telefono (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_usuario INT NOT NULL
    REFERENCES usuario(id) ON DELETE CASCADE,
  telefono VARCHAR(20) NOT NULL
);

CREATE TABLE cancha (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_instalacion INT NOT NULL
    REFERENCES instalacion(id) ON DELETE CASCADE,
  id_deporte INT NOT NULL
    REFERENCES deporte(id) ON DELETE RESTRICT,
  precio_por_hora NUMERIC(8,2) NOT NULL CHECK (precio_por_hora>=0),
  capacidad INT NOT NULL CHECK (capacidad>0),
  iluminacion BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE(nombre,id_instalacion)
);

CREATE TABLE cancha_foto (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_cancha INT NOT NULL
    REFERENCES cancha(id) ON DELETE CASCADE,
  url VARCHAR(255) NOT NULL
);

CREATE TABLE horario (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  dia_semana INT NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  CHECK (hora_fin>hora_inicio)
);

CREATE TABLE cancha_horario (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_cancha INT NOT NULL
    REFERENCES cancha(id) ON DELETE CASCADE,
  id_horario INT NOT NULL
    REFERENCES horario(id) ON DELETE CASCADE,
  UNIQUE(id_cancha,id_horario)
);

CREATE TABLE servicio_adicional (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  descripcion VARCHAR(100) NOT NULL,
  precio NUMERIC(8,2) NOT NULL CHECK (precio>=0)
);

CREATE TABLE reserva (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_usuario INT NOT NULL
    REFERENCES usuario(id) ON DELETE CASCADE,
  id_cancha INT NOT NULL
    REFERENCES cancha(id) ON DELETE CASCADE,
  fecha DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  duracion NUMERIC(5,2),
  estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
  CHECK (hora_fin>hora_inicio)
);

CREATE TABLE reserva_servicio (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_reserva INT NOT NULL
    REFERENCES reserva(id) ON DELETE CASCADE,
  id_servicio INT NOT NULL
    REFERENCES servicio_adicional(id) ON DELETE RESTRICT,
  UNIQUE(id_reserva,id_servicio)
);

CREATE TABLE pago (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_reserva INT NOT NULL UNIQUE
    REFERENCES reserva(id) ON DELETE CASCADE,
  fecha_pago TIMESTAMP NOT NULL DEFAULT NOW(),
  total NUMERIC(10,2) NOT NULL CHECK (total>=0)
);

CREATE TABLE valoracion (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_usuario INT NOT NULL
    REFERENCES usuario(id) ON DELETE CASCADE,
  id_cancha INT NOT NULL
    REFERENCES cancha(id) ON DELETE CASCADE,
  puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
  comentarios TEXT,
  fecha_valoracion TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(id_usuario,id_cancha)
);
