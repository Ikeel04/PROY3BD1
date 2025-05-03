-- ─────────────────────────────────────────────────────────────────────────────
-- 3) DATOS DE PRUEBA (≥100 filas)
-- ─────────────────────────────────────────────────────────────────────────────

TRUNCATE TABLE
  cancha_horario, reserva_servicio, pago, valoracion, reserva,
  cancha_foto, cancha, horario, servicio_adicional,
  usuario_telefono, usuario, deporte, instalacion, ciudad
RESTART IDENTITY CASCADE;

-- 3.1 a 3.6 como antes (ciudad→usuario_telefono)…
INSERT INTO ciudad(nombre)       SELECT 'Ciudad '||i FROM generate_series(1,100)i;
INSERT INTO instalacion(nombre,direccion,id_ciudad)
  SELECT 'Instalacion '||i,'Dir '||i,((i-1)%100)+1 FROM generate_series(1,100)i;
INSERT INTO deporte(nombre)      SELECT 'Deporte '||i FROM generate_series(1,100)i;
INSERT INTO usuario(nombre,email,password_hash)
  SELECT 'Usuario '||i,'u'||i||'@ex.com','pass'||i FROM generate_series(1,100)i;
INSERT INTO usuario_telefono(id_usuario,telefono)
  SELECT ((i-1)%100)+1,'555-'||LPAD(i::text,3,'0') FROM generate_series(1,100)i;
INSERT INTO servicio_adicional(descripcion,precio)
  SELECT 'Serv '||i,(floor(random()*50)+10)::numeric(8,2) FROM generate_series(1,100)i;

-- 3.7 Horarios (1h sin solapamiento interno)
INSERT INTO horario(dia_semana,hora_inicio,hora_fin)
SELECT (floor(random()*7)+1)::int,
       hi.hora,(hi.hora+interval '1 hour')::time
FROM generate_series(1,100)i
CROSS JOIN LATERAL (SELECT make_time((floor(random()*14)+6)::int,0,0) AS hora) AS hi;

-- 3.8 a 3.9 (canchas + fotos)
INSERT INTO cancha(nombre,id_instalacion,id_deporte,precio_por_hora,capacidad,iluminacion)
 SELECT 'Cancha '||i,((i-1)%100)+1,((i-1)%100)+1,(random()*30+20)::numeric(8,2),
        (floor(random()*20)+5)::int,(random()<0.5)
 FROM generate_series(1,100)i;

INSERT INTO cancha_foto(id_cancha,url)
 SELECT ((i-1)%100)+1,'https://img/'||i||'.jpg'
 FROM generate_series(1,100)i;

-- 3.10 Reservas: UNA POR CANCHA → no hay solapamiento
INSERT INTO reserva(id_usuario,id_cancha,fecha,hora_inicio,hora_fin,estado)
SELECT
  ((i-1)%100)+1,               -- usuario distinto
  i,                            -- cancha única i∈[1..100]
  CURRENT_DATE + ((i-1)%30),    -- fecha varía 30 días
  make_time(6,0,0),             -- siempre 06:00–07:00
  make_time(7,0,0),
  'confirmada'
FROM generate_series(1,100)i;

-- 3.11 Reserva–Servicio
INSERT INTO reserva_servicio(id_reserva,id_servicio)
 SELECT i,((i-1)%100)+1 FROM generate_series(1,100)i;

-- 3.12 Cancha–Horario
INSERT INTO cancha_horario(id_cancha,id_horario)
 SELECT i,((i-1)%100)+1 FROM generate_series(1,100)i;

-- 3.13 Valoraciones
INSERT INTO valoracion(id_usuario,id_cancha,puntuacion,comentarios)
 SELECT ((i-1)%100)+1,((i*7-1)%100)+1,(floor(random()*5)+1)::int,'C'||i
 FROM generate_series(1,100)i;

-- 3.14 Pagos (dispara trigger)
INSERT INTO pago(id_reserva) SELECT generate_series(1,100);