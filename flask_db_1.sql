--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.10
-- Dumped by pg_dump version 9.5.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS flask_db_1;
--
-- Name: flask_db_1; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE flask_db_1 WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'ru_RU.UTF-8' LC_CTYPE = 'ru_RU.UTF-8';


ALTER DATABASE flask_db_1 OWNER TO postgres;

\connect flask_db_1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: citext; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;


--
-- Name: EXTENSION citext; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';


SET search_path = public, pg_catalog;

--
-- Name: my_to_char(timestamp without time zone, text); Type: FUNCTION; Schema: public; Owner: igor
--

CREATE FUNCTION my_to_char(some_time timestamp without time zone, format text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $_$
    select to_char($1, $2);
$_$;


ALTER FUNCTION public.my_to_char(some_time timestamp without time zone, format text) OWNER TO igor;

--
-- Name: my_to_char(timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: igor
--

CREATE FUNCTION my_to_char(some_time timestamp with time zone, format text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $_$
    select to_char($1, $2);
$_$;


ALTER FUNCTION public.my_to_char(some_time timestamp with time zone, format text) OWNER TO igor;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: db_active_users; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_active_users (
    active_user_id bigint NOT NULL,
    forum citext NOT NULL,
    nickname citext NOT NULL
);


ALTER TABLE db_active_users OWNER TO igor;

--
-- Name: db_active_users_active_user_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_active_users_active_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_active_users_active_user_id_seq OWNER TO igor;

--
-- Name: db_active_users_active_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_active_users_active_user_id_seq OWNED BY db_active_users.active_user_id;


--
-- Name: db_forums; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_forums (
    forum_id bigint NOT NULL,
    slug citext NOT NULL,
    title citext NOT NULL,
    user_creator citext NOT NULL,
    posts integer DEFAULT 0 NOT NULL,
    threads integer DEFAULT 0 NOT NULL
);


ALTER TABLE db_forums OWNER TO igor;

--
-- Name: db_forums_forum_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_forums_forum_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_forums_forum_id_seq OWNER TO igor;

--
-- Name: db_forums_forum_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_forums_forum_id_seq OWNED BY db_forums.forum_id;


--
-- Name: db_max_post_id; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_max_post_id (
    max_id bigint,
    id integer DEFAULT 0
);


ALTER TABLE db_max_post_id OWNER TO igor;

--
-- Name: db_posts; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_posts (
    id bigint NOT NULL,
    author citext NOT NULL,
    created timestamp with time zone,
    forum citext NOT NULL,
    isedited boolean DEFAULT false NOT NULL,
    message text NOT NULL,
    parent bigint DEFAULT 0 NOT NULL,
    thread integer NOT NULL,
    mpath integer[]
);


ALTER TABLE db_posts OWNER TO igor;

--
-- Name: db_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_posts_id_seq OWNER TO igor;

--
-- Name: db_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_posts_id_seq OWNED BY db_posts.id;


--
-- Name: db_threads; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_threads (
    id integer NOT NULL,
    author citext NOT NULL,
    created timestamp with time zone,
    forum citext,
    message text NOT NULL,
    title citext NOT NULL,
    votes integer DEFAULT 0,
    slug citext DEFAULT NULL::character varying,
    posts bigint DEFAULT 0 NOT NULL
);


ALTER TABLE db_threads OWNER TO igor;

--
-- Name: db_threads_thread_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_threads_thread_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_threads_thread_id_seq OWNER TO igor;

--
-- Name: db_threads_thread_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_threads_thread_id_seq OWNED BY db_threads.id;


--
-- Name: db_users; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_users (
    user_id bigint NOT NULL,
    about text,
    email citext NOT NULL,
    fullname citext NOT NULL,
    nickname citext NOT NULL
);


ALTER TABLE db_users OWNER TO igor;

--
-- Name: db_users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_users_user_id_seq OWNER TO igor;

--
-- Name: db_users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_users_user_id_seq OWNED BY db_users.user_id;


--
-- Name: db_votes; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE db_votes (
    vote_id bigint NOT NULL,
    thread_slug citext,
    nickname citext NOT NULL,
    voice integer NOT NULL,
    thread_id integer NOT NULL
);


ALTER TABLE db_votes OWNER TO igor;

--
-- Name: db_votes_vote_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE db_votes_vote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE db_votes_vote_id_seq OWNER TO igor;

--
-- Name: db_votes_vote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE db_votes_vote_id_seq OWNED BY db_votes.vote_id;


--
-- Name: test_result_votes; Type: TABLE; Schema: public; Owner: igor
--

CREATE TABLE test_result_votes (
    thread_id integer,
    nickname citext,
    old_voice integer,
    new_voice integer,
    old_threads_votes integer,
    returning_votes integer,
    test_result_id bigint NOT NULL,
    thread_slug citext,
    "thread votes from update" integer,
    slug_or_id citext,
    forum_slug citext,
    "thread author" citext
);


ALTER TABLE test_result_votes OWNER TO igor;

--
-- Name: test_result_votes_test_result_id_seq; Type: SEQUENCE; Schema: public; Owner: igor
--

CREATE SEQUENCE test_result_votes_test_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE test_result_votes_test_result_id_seq OWNER TO igor;

--
-- Name: test_result_votes_test_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: igor
--

ALTER SEQUENCE test_result_votes_test_result_id_seq OWNED BY test_result_votes.test_result_id;


--
-- Name: active_user_id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_active_users ALTER COLUMN active_user_id SET DEFAULT nextval('db_active_users_active_user_id_seq'::regclass);


--
-- Name: forum_id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_forums ALTER COLUMN forum_id SET DEFAULT nextval('db_forums_forum_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_posts ALTER COLUMN id SET DEFAULT nextval('db_posts_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_threads ALTER COLUMN id SET DEFAULT nextval('db_threads_thread_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_users ALTER COLUMN user_id SET DEFAULT nextval('db_users_user_id_seq'::regclass);


--
-- Name: vote_id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_votes ALTER COLUMN vote_id SET DEFAULT nextval('db_votes_vote_id_seq'::regclass);


--
-- Name: test_result_id; Type: DEFAULT; Schema: public; Owner: igor
--

ALTER TABLE ONLY test_result_votes ALTER COLUMN test_result_id SET DEFAULT nextval('test_result_votes_test_result_id_seq'::regclass);


--
-- Data for Name: db_active_users; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_active_users_active_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_active_users_active_user_id_seq', 989608, true);


--
-- Data for Name: db_forums; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_forums_forum_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_forums_forum_id_seq', 17049, true);


--
-- Data for Name: db_max_post_id; Type: TABLE DATA; Schema: public; Owner: igor
--

INSERT INTO db_max_post_id VALUES (185581, 0);


--
-- Data for Name: db_posts; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_posts_id_seq', 216184, true);


--
-- Data for Name: db_threads; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_threads_thread_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_threads_thread_id_seq', 955543, true);


--
-- Data for Name: db_users; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_users_user_id_seq', 162007, true);


--
-- Data for Name: db_votes; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: db_votes_vote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('db_votes_vote_id_seq', 32670, true);


--
-- Data for Name: test_result_votes; Type: TABLE DATA; Schema: public; Owner: igor
--



--
-- Name: test_result_votes_test_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: igor
--

SELECT pg_catalog.setval('test_result_votes_test_result_id_seq', 11519, true);


--
-- Name: db_active_users_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_active_users
    ADD CONSTRAINT db_active_users_pkey PRIMARY KEY (active_user_id);


--
-- Name: db_forums_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_forums
    ADD CONSTRAINT db_forums_pkey PRIMARY KEY (forum_id);


--
-- Name: db_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_posts
    ADD CONSTRAINT db_posts_pkey PRIMARY KEY (id);


--
-- Name: db_threads_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_threads
    ADD CONSTRAINT db_threads_pkey PRIMARY KEY (id);


--
-- Name: db_users_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_users
    ADD CONSTRAINT db_users_pkey PRIMARY KEY (user_id);


--
-- Name: db_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_votes
    ADD CONSTRAINT db_votes_pkey PRIMARY KEY (vote_id);


--
-- Name: db_active_users_idx_nickname; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_active_users_idx_nickname ON db_active_users USING btree (nickname);


--
-- Name: db_forums_forum_id_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_forums_forum_id_uindex ON db_forums USING btree (forum_id);


--
-- Name: db_forums_idx_slug; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_forums_idx_slug ON db_forums USING btree (slug, forum_id, title, user_creator, posts, threads);


--
-- Name: db_forums_slug_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_forums_slug_uindex ON db_forums USING btree (slug);


--
-- Name: db_posts_idx_created_and_id; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_posts_idx_created_and_id ON db_posts USING btree (created, id);


--
-- Name: db_posts_idx_forum; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_posts_idx_forum ON db_posts USING btree (forum);


--
-- Name: db_posts_idx_parent; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_posts_idx_parent ON db_posts USING btree (parent);


--
-- Name: db_posts_idx_parent_thread_path; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_posts_idx_parent_thread_path ON db_posts USING btree (parent, thread, (mpath[1]));


--
-- Name: db_posts_idx_thread; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_posts_idx_thread ON db_posts USING btree (thread);


--
-- Name: db_threads_idx_forum_created; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_threads_idx_forum_created ON db_threads USING btree (forum, created);


--
-- Name: db_threads_slug_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_threads_slug_uindex ON db_threads USING btree (slug);


--
-- Name: db_threads_thread_id_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_threads_thread_id_uindex ON db_threads USING btree (id);


--
-- Name: db_users_email_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_users_email_uindex ON db_users USING btree (email);


--
-- Name: db_users_nickname_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_users_nickname_uindex ON db_users USING btree (nickname);


--
-- Name: db_users_user_id_uindex; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX db_users_user_id_uindex ON db_users USING btree (user_id);


--
-- Name: db_votes_idx_thread_id_and_nickname; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_votes_idx_thread_id_and_nickname ON db_votes USING btree (thread_id, nickname);


--
-- Name: db_votes_idx_thread_slug_and_nickname; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX db_votes_idx_thread_slug_and_nickname ON db_votes USING btree (thread_slug, nickname);


--
-- Name: idx_db_max_post_id; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX idx_db_max_post_id ON db_max_post_id USING btree (max_id);


--
-- Name: idx_db_max_post_id_id; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX idx_db_max_post_id_id ON db_max_post_id USING btree (id, max_id);


--
-- Name: idx_round_db_active_users; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX idx_round_db_active_users ON db_active_users USING btree (forum, nickname);


--
-- Name: idx_round_db_votes; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX idx_round_db_votes ON db_votes USING btree (thread_id, nickname, voice);


--
-- Name: idx_uniq_nickname_thread_id; Type: INDEX; Schema: public; Owner: igor
--

CREATE UNIQUE INDEX idx_uniq_nickname_thread_id ON db_votes USING btree (nickname, thread_id);


--
-- Name: idx_users_nickname_user_id; Type: INDEX; Schema: public; Owner: igor
--

CREATE INDEX idx_users_nickname_user_id ON db_users USING btree (nickname, user_id);


--
-- Name: db_active_users_db_users_nickname_fk; Type: FK CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_active_users
    ADD CONSTRAINT db_active_users_db_users_nickname_fk FOREIGN KEY (nickname) REFERENCES db_users(nickname) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: db_votes_db_threads_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_votes
    ADD CONSTRAINT db_votes_db_threads_id_fk FOREIGN KEY (thread_id) REFERENCES db_threads(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: db_votes_db_users_nickname_fk; Type: FK CONSTRAINT; Schema: public; Owner: igor
--

ALTER TABLE ONLY db_votes
    ADD CONSTRAINT db_votes_db_users_nickname_fk FOREIGN KEY (nickname) REFERENCES db_users(nickname) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

