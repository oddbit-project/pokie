CREATE TABLE IF NOT EXISTS articles (
    article_id serial PRIMARY KEY,
    title character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    body text,
    author_name character varying(50),
    status character varying(20) DEFAULT 'draft',
    created_at timestamp DEFAULT now()
);
