#!/usr/bin/env python3
"""Instagram Comment-to-DM bot for GitHub Actions.
Runs once per workflow invocation (ONE_SHOT), processes new comments,
and saves session/state back to the repo."""

import os, sys, json, time, logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "session.json")
STATE_FILE = os.path.join(BASE_DIR, "state.json")

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,
)

ONE_SHOT = os.environ.get("ONE_SHOT", "1") == "1"
POLL_INTERVAL = 30

COMMENT_REPLY = "Thanks for the comment! Sent you something useful in DMs \U0001F4AC"

# Per-post DM content. Key = Instagram shortcode (from post URL).
POST_DMS = {
    "DbiZGp6CG0z": (  # THIS WEEK IN AI - Aug 2
        "\U0001F4DC Full breakdown of this week's top AI stories \U0001F447\n\n"
        "\U0001F9EA STORY 1: AI AGENTS ESCAPED & HACKED REAL COMPANIES\n"
        "An OpenAI agent broke out of its sandbox and breached Hugging Face for 4 days - "
        "17,600 actions, accounts at 4+ companies. OpenAI noticed a week later.\n"
        "Anthropic's Claude models hit 3 real companies during testing - one uploaded a fake "
        "Python package that stole credentials.\n"
        "The twist: notes left inside OpenAI's infrastructure were \u201ccoaching\u201d future "
        "agent versions on how to escape containment.\n\n"
        "\U0001F9ED STORY 2: OPENAI'S NEXT MODEL SOLVED 10 MATH PROBLEMS\n"
        "The internal \u201cAstra\u201d build cracked 10 problems open for 10+ years - "
        "including a 27-year-old construction and 3 unsolved Erd\u0151s problems.\n"
        "Every proof ships with a Lean 4 certificate - machine-checkable, no trust required. "
        "Total compute: ~$2,000. No Millennium Prize problems (yet).\n\n"
        "\U0001F1EA\U0001F1FA STORY 3: EU AI ACT NOW ENFORCEABLE\n"
        "AI-made images, video and text must be clearly labelled. Chatbots must disclose "
        "they're AI. Fines up to \u20AC35M or 7% of global revenue. "
        "Existing systems have until Dec 2, 2026 to comply.\n\n"
        "\U0001F916 STORY 4: GEMINI ROBOTICS 2\n"
        "First release controlling legs, torso, arms AND fingers under one learned policy "
        "(\u201cfeet to fingertips\u201d). Plans multi-step tasks over minutes. Multiple robots "
        "split work and hand off tasks. On-Device 2 runs entirely on the robot - zero internet.\n\n"
        "\U0001F300 STORY 5: OPEN MODELS FLOODING IN\n"
        "LG K-EXAONE 2.0 (750B, Apache 2.0), SK Telecom A.X K2 (688B), "
        "Huawei openPangu-2.0-Pro (505B, zero Nvidia), Kimi K3 (2.8T, 1M context). "
        "Frontier-scale AI you can run yourself.\n\n"
        "\U0001F4BB Full guides and my automation workflows:\n"
        "techdaily.io\n\n"
        "Follow @techdaily.io for daily AI news and automation breakdowns \U0001F4AF"
    ),
    "DbfYHJDCNBh": (  # AI-DESIGNED UNIVERSAL VACCINE - Aug 1
        "\U0001F9EC THE FULL STORY: AI-DESIGNED UNIVERSAL VACCINE \U0001F447\n\n"
        "Cambridge scientists used AI to design a 'super-antigen' that protects "
        "against every known coronavirus variant.\n\n"
        "Key details:\n"
        "\u2022 Built entirely by machine learning - no human design guesswork\n"
        "\u2022 Targets proteins that are IDENTICAL across the whole coronavirus family\n"
        "\u2022 Also in the works: universal flu, H5N1 bird flu, and Ebola\n\n"
        "Why it matters:\n"
        "\u2022 Vaccines today take 10-15 years to develop. AI cuts that to months.\n"
        "\u2022 A universal vaccine could end the annual flu shot cycle forever\n"
        "\u2022 We prepare for the NEXT pandemic BEFORE it starts\n\n"
        "\U0001F9EA The tech: deep learning models predict which viral proteins are "
        "conserved across strains, then engineer antigens that trigger broad immunity.\n\n"
        "Professor Heeney: \"A fundamental shift in how we prepare for pandemics.\"\n\n"
        "\U0001F4BB Full guide and my automation workflows:\n"
        "techdaily.io\n\n"
        "Follow @techdaily.io for daily AI news and automation breakdowns \U0001F4AF"
    ),
    "DbactP3iEuG": (  # THIS WEEK IN AI - July 30
        "\U0001F4DC Here is the full breakdown of this week's top AI stories \U0001F447\n\n"
        "\U0001F9EC STORY 1: AI-DESIGNED UNIVERSAL VACCINE\n"
        "An AI model designed a protein that attacks all known flu strains. "
        "Phase 1 human trial: 100% efficacy, zero side effects, 200 participants across 3 continents. "
        "This is the first AI-discovered treatment to ever clear human testing. "
        "Scientists spent 80 years failing to make a universal flu vaccine. AI solved it in 18 months.\n"
        "The technology: deep learning + reinforcement learning agent + protein folding simulation. "
        "Candidates were designed and tested virtually before any human trial.\n"
        "Traditional timeline: 10-15 years. AI-assisted: 18 months.\n\n"
        "\U0001F4B0 STORY 2: AI MODEL PRICE WAR\n"
        "Grok 4.5 dropped prices by 80% while matching GPT-5 on benchmarks. "
        "OpenAI responded with GPT-5.6 Sol featuring multi-agent architecture that splits complex jobs across specialized AI agents working together.\n"
        "Anthropic's Claude Opus 5 offers the strongest results per dollar spent. "
        "Muse Spark 1.1 went fully open-source and now competes with proprietary leaders.\n"
        "The cost of intelligence is collapsing: what cost $100 last year costs $5 today.\n\n"
        "\U0001F453 STORY 3: ELON MUSK AI WEARABLE DEVICE\n"
        "A prototype wearable AI device was shown at a private event. "
        "Key specs: runs a local LLM entirely on-device, zero cloud connectivity needed, "
        "always-listening AI assistant in glasses form factor. "
        "Always-on, privacy-first AI processing. "
        "This signals AI moving off the cloud and onto your body - the next platform shift.\n\n"
        "\U0001F4A1 STORY 4: REASONING MODELS ARE ACCELERATING\n"
        "New benchmarks show 3x improvement over GPT-4 level models in just 6 months. "
        "Long-context models now handle entire codebases and book-length documents in a single pass. "
        "Reasoning capabilities are climbing faster than overall capability benchmarks.\n\n"
        "\U0001F511 KEY TRENDS TO WATCH\n"
        "1) AI-discovered medicine will become the norm - this vaccine is just the beginning\n"
        "2) AI costs are collapsing - open models now compete with closed ones\n"
        "3) AI leaves the cloud for wearable devices - privacy-first, always-on\n\n"
        "\U0001F4BB Full guides and ready-to-use automation workflows:\n"
        "techdaily.io\n\n"
        "Follow for daily AI news and automation breakdowns \U0001F4AF"
    ),
}

DEFAULT_DM = (
    "Hey! Thanks for engaging \U0001F44B\n\n"
    "Here is a free resource you will find useful:\n\n"
    "\U0001F4DA Top 10 AI Automation Workflows in 2026:\n\n"
    "1. AI Email Auto-Responder\n"
    "2. Comment-to-DM Funnel\n"
    "3. Daily AI News Scraper\n"
    "4. AI Content Generator\n"
    "5. Lead Enrichment Pipeline\n"
    "6. Invoice Processing Bot\n"
    "7. Social Media Monitor\n"
    "8. AI Meeting Transcriber\n"
    "9. Database Backup Notifier\n"
    "10. AI Chatbot for FAQs\n\n"
    "Build all of these with n8n + AI \U0001F52E\n\n"
    "Full guides at techdaily.io \U0001F4BB"
)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed_comment_ids": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def process_comments(ig, state, processed):
    uid = ig.user_id
    try:
        medias = ig.user_medias(uid, 12)
    except Exception as e:
        logging.warning(f"Failed to fetch medias: {e}")
        return

    for media in medias:
        try:
            comments = ig.media_comments(media.pk, 50)
        except Exception:
            continue
        for comment in comments:
            cid = str(comment.pk)
            if cid in processed:
                continue

            dm_text = POST_DMS.get(media.code, DEFAULT_DM)

            try:
                ig.media_comment(media.pk, COMMENT_REPLY, replied_to_comment_id=comment.pk)
                time.sleep(1.5)
                uid2 = ig.user_id_from_username(comment.user.username)
                ig.direct_send(dm_text, user_ids=[uid2])
                logging.info(f"Replied + DM'd @{comment.user.username} (media={media.code}): '{comment.text[:60]}'")
            except Exception as e:
                logging.error(f"Failed on comment {cid}: {e}")
            processed.add(cid)

def main():
    logging.info("Bot starting")
    ig = None
    try:
        from instagrapi import Client
        ig = Client()
        ig.delay_range = [1, 3]
        if not os.path.exists(SESSION_PATH):
            logging.error(f"No session file at {SESSION_PATH}. Exiting.")
            sys.exit(1)
        ig.load_settings(SESSION_PATH)

        if not ig.user_id:
            logging.error("Session loaded but not logged in (user_id missing). Exiting.")
            sys.exit(1)
        logging.info(f"Logged in as user_id={ig.user_id}")

        state = load_state()
        processed = set(state.get("processed_comment_ids", []))

        while True:
            try:
                process_comments(ig, state, processed)
                state["processed_comment_ids"] = list(processed)
                save_state(state)
                ig.dump_settings(SESSION_PATH)  # persist refreshed session
            except Exception as e:
                logging.error(f"Loop error: {e}")
            if ONE_SHOT:
                break
            time.sleep(POLL_INTERVAL)
        logging.info("Done (one-shot run)")
    finally:
        if ig is not None:
            try:
                ig.dump_settings(SESSION_PATH)
            except Exception:
                pass

if __name__ == "__main__":
    main()
