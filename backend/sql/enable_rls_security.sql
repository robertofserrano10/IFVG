-- Enable RLS on all public tables.
-- Backend uses service_role key and bypasses RLS automatically.
-- No permissive public policies needed.

ALTER TABLE trading_days ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_bias ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_images ENABLE ROW LEVEL SECURITY;
