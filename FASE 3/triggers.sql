-- A) Duración de reserva (horas)
CREATE OR REPLACE FUNCTION fn_calcular_duracion() RETURNS trigger AS $$
BEGIN
  NEW.duracion := EXTRACT(EPOCH FROM (NEW.hora_fin - NEW.hora_inicio))/3600;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_duracion
BEFORE INSERT OR UPDATE ON reserva
FOR EACH ROW EXECUTE FUNCTION fn_calcular_duracion();

-- B) Evitar solapamiento (fecha+hora)
CREATE OR REPLACE FUNCTION fn_evitar_solaplamiento() RETURNS trigger AS $$
DECLARE
  nuevo tsrange := tsrange(
    (NEW.fecha+NEW.hora_inicio)::timestamp,
    (NEW.fecha+NEW.hora_fin )::timestamp
  );
BEGIN
  IF EXISTS (
    SELECT 1 FROM reserva r
     WHERE r.id_cancha=NEW.id_cancha
       AND r.id<>COALESCE(NEW.id,0)
       AND tsrange((r.fecha+r.hora_inicio)::timestamp,(r.fecha+r.hora_fin)::timestamp) && nuevo
  ) THEN
    RAISE EXCEPTION 'La reserva se solapa con otra existente';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_evitar_solaplamiento
BEFORE INSERT OR UPDATE ON reserva
FOR EACH ROW EXECUTE FUNCTION fn_evitar_solaplamiento();

-- C) Cálculo de pago total
CREATE OR REPLACE FUNCTION fn_calcular_pago_total() RETURNS trigger AS $$
DECLARE precio_h NUMERIC;
BEGIN
  SELECT c.precio_por_hora INTO precio_h
    FROM reserva r JOIN cancha c ON r.id_cancha=c.id
   WHERE r.id=NEW.id_reserva;

  NEW.total := 
    (SELECT duracion FROM reserva WHERE id=NEW.id_reserva)*precio_h
    + COALESCE((
        SELECT SUM(sa.precio)
        FROM reserva_servicio rs
        JOIN servicio_adicional sa ON rs.id_servicio=sa.id
       WHERE rs.id_reserva=NEW.id_reserva
      ),0);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_pago
BEFORE INSERT OR UPDATE ON pago
FOR EACH ROW EXECUTE FUNCTION fn_calcular_pago_total();
