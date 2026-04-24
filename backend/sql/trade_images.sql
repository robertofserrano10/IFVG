CREATE TABLE trade_images (
  id         bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  trade_id   bigint NOT NULL REFERENCES trades(id) ON DELETE CASCADE,
  image_url  text NOT NULL,
  image_type text NOT NULL CHECK (image_type IN ('entrada', 'salida', 'contexto')),
  created_at timestamptz NOT NULL DEFAULT now()
);
