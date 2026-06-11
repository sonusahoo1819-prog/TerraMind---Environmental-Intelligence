-- TerraMind PostgreSQL Database Schema for Supabase

-- Drop existing tables if they conflict (Warning: drops all data)
DROP TABLE IF EXISTS public.transactions CASCADE;
DROP TABLE IF EXISTS public.user_challenges CASCADE;
DROP TABLE IF EXISTS public.challenges CASCADE;
DROP TABLE IF EXISTS public.chat_history CASCADE;
DROP TABLE IF EXISTS public.carbon_logs CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- 1. Users Table
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    carbon_score INTEGER DEFAULT 82,
    xp INTEGER DEFAULT 24500,
    level INTEGER DEFAULT 24,
    credits INTEGER DEFAULT 4500,
    trees INTEGER DEFAULT 8,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Carbon Logs Table
CREATE TABLE public.carbon_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    public_transport INTEGER DEFAULT 0,
    renewable_energy INTEGER DEFAULT 0,
    diet VARCHAR(50) DEFAULT 'Veggie',
    commuting_mode VARCHAR(50) DEFAULT 'Electric',
    transport_emissions REAL DEFAULT 0.0,
    energy_emissions REAL DEFAULT 0.0,
    diet_emissions REAL DEFAULT 0.0,
    total_emissions REAL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Chat History Table
CREATE TABLE public.chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    sender VARCHAR(50) NOT NULL, -- 'user' or 'ai'
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Challenges Table
CREATE TABLE public.challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    reward_xp INTEGER NOT NULL,
    reward_credits INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL
);

-- 5. User Challenges Table
CREATE TABLE public.user_challenges (
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    challenge_id INTEGER REFERENCES public.challenges(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, challenge_id)
);

-- 6. Transactions Table
CREATE TABLE public.transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    item_title VARCHAR(255) NOT NULL,
    cost_credits INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS (Optional: Set policies if enabling)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.carbon_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- Allow all read/write operations for testing purposes (public anon access)
CREATE POLICY "Allow anon read user" ON public.users FOR SELECT USING (true);
CREATE POLICY "Allow anon update user" ON public.users FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow anon insert user" ON public.users FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon read carbon_logs" ON public.carbon_logs FOR SELECT USING (true);
CREATE POLICY "Allow anon insert carbon_logs" ON public.carbon_logs FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon read chat_history" ON public.chat_history FOR SELECT USING (true);
CREATE POLICY "Allow anon insert chat_history" ON public.chat_history FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon read challenges" ON public.challenges FOR SELECT USING (true);

CREATE POLICY "Allow anon read user_challenges" ON public.user_challenges FOR SELECT USING (true);
CREATE POLICY "Allow anon write user_challenges" ON public.user_challenges FOR ALL USING (true);

CREATE POLICY "Allow anon read transactions" ON public.transactions FOR SELECT USING (true);
CREATE POLICY "Allow anon insert transactions" ON public.transactions FOR INSERT WITH CHECK (true);


-- ==========================================
-- SEED DATA SETUP
-- ==========================================

-- Seed default user
INSERT INTO public.users (id, username, email, carbon_score, xp, level, credits, trees)
VALUES (1, 'Guest Explorer', 'guest@terramind.eco', 82, 24500, 24, 4500, 8)
ON CONFLICT (id) DO NOTHING;

-- Reset SERIAL counter for users
SELECT setval('public.users_id_seq', (SELECT MAX(id) FROM public.users));

-- Seed challenges
INSERT INTO public.challenges (id, title, description, reward_xp, reward_credits, category) VALUES
(1, 'Eco Commuter', 'Log 5 public transport trips instead of driving this week.', 300, 150, 'Transport'),
(2, 'Green Chef', 'Cook plant-based meals for 3 consecutive days.', 250, 100, 'Diet'),
(3, 'Power Saver', 'Reduce home energy consumption by 10% this month.', 500, 250, 'Energy'),
(4, 'Waste Warrior', 'Compost organic waste for a week.', 200, 100, 'Waste')
ON CONFLICT (id) DO NOTHING;

-- Reset SERIAL counter for challenges
SELECT setval('public.challenges_id_seq', (SELECT MAX(id) FROM public.challenges));

-- Seed user challenges
INSERT INTO public.user_challenges (user_id, challenge_id, completed, progress) VALUES
(1, 1, FALSE, 3),
(1, 2, TRUE, 3),
(1, 3, FALSE, 0),
(1, 4, FALSE, 0)
ON CONFLICT (user_id, challenge_id) DO NOTHING;

-- Seed historical carbon logs
INSERT INTO public.carbon_logs (user_id, date, public_transport, renewable_energy, diet, commuting_mode, transport_emissions, energy_emissions, diet_emissions, total_emissions) VALUES
(1, CURRENT_DATE - INTERVAL '6 days', 20, 10, 'Omnivore', 'Gas Car', 2.5, 1.8, 1.2, 5.5),
(1, CURRENT_DATE - INTERVAL '5 days', 25, 15, 'Flexi', 'Gas Car', 2.2, 1.6, 0.9, 4.7),
(1, CURRENT_DATE - INTERVAL '4 days', 30, 20, 'Flexi', 'Electric', 1.8, 1.5, 0.9, 4.2),
(1, CURRENT_DATE - INTERVAL '3 days', 40, 30, 'Veggie', 'Electric', 1.2, 1.2, 0.5, 2.9),
(1, CURRENT_DATE - INTERVAL '2 days', 45, 30, 'Veggie', 'Electric', 0.9, 1.2, 0.5, 2.6),
(1, CURRENT_DATE - INTERVAL '1 day', 45, 30, 'Veggie', 'Electric', 0.9, 1.2, 0.5, 2.6)
ON CONFLICT DO NOTHING;

-- Seed introductory chat history
INSERT INTO public.chat_history (user_id, sender, message) VALUES
(1, 'ai', 'Welcome to TerraMind, Guest Explorer! I am your EcoCoach AI. Let me know if you want tips on reducing your emissions or optimizing your daily sustainability habits.')
ON CONFLICT DO NOTHING;
