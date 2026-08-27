# Common fields

ARTIST_CATEGORIES = {
    "photographer",
    "musician",
    "video_editor",
}

EVIDENCE_STATUS = {
    "demonstrated",
    "claimed_only",
    "conflicting",
    "unknown",
}


# Photographer

PHOTOGRAPHER_SCHEMA = {
    "category": "photographer",

    "capability_dimensions": {
        "subject_domains": {
            "description": "Subjects or domains the supplied work demonstrates.",
            "examples": [
                "portrait",
                "product",
                "food",
                "fashion",
                "event",
                "architecture",
                "interior",
                "hospitality",
                "travel",
                "nature",
                "lifestyle",
            ],
        },

        "visual_style": {
            "description": "Observable visual treatment and aesthetic style.",
            "examples": [
                "clean",
                "premium",
                "editorial",
                "natural",
                "documentary",
                "candid",
                "cinematic",
                "minimal",
                "dramatic",
                "bright",
            ],
        },

        "composition": {
            "description": "Observable composition approaches used in the work.",
            "examples": [
                "close_up",
                "wide_composition",
                "group_composition",
                "environmental_portrait",
                "symmetry",
                "layered_composition",
                "product_isolation",
            ],
        },

        "lighting": {
            "description": "Lighting approaches demonstrated by the supplied work.",
            "examples": [
                "natural_light",
                "studio_style",
                "soft_light",
                "hard_light",
                "directional_light",
                "controlled_lighting",
                "ambient_event_lighting",
                "low_light",
            ],
        },

        "environment": {
            "description": "Shooting environments demonstrated by the work.",
            "examples": [
                "studio",
                "indoor",
                "outdoor",
                "on_location",
                "event_venue",
                "commercial_setup",
            ],
        },

        "people_direction": {
            "description": "Types of people-focused photography demonstrated.",
            "examples": [
                "candid_interaction",
                "group_photography",
                "posed_portrait",
                "headshot",
                "event_coverage",
                "reaction_or_action_moments",
            ],
        },

        "technical_execution": {
            "description": "Observable technical execution in the supplied work.",
            "examples": [
                "exposure",
                "focus",
                "sharpness",
                "lighting_control",
                "color_consistency",
                "retouching",
                "detail_preservation",
            ],
        },

        "deliverable_formats": {
            "description": "Output formats that are demonstrated or explicitly supported.",
            "examples": [
                "square",
                "vertical",
                "horizontal",
                "social_media",
                "web",
            ],
        },

        "use_cases": {
            "description": "Commercial or practical use cases demonstrated by the work.",
            "examples": [
                "commercial",
                "social_media",
                "events",
                "editorial",
                "hospitality",
                "product_marketing",
            ],
        },
    },
}


# Musician

MUSICIAN_SCHEMA = {
    "category": "musician",

    "capability_dimensions": {
        "artist_format": {
            "description": "Performance format demonstrated by the artist.",
            "examples": [
                "solo",
                "duo",
                "band",
                "electronic_live_act",
            ],
        },

        "role": {
            "description": "Musical roles demonstrated or explicitly supported.",
            "examples": [
                "vocalist",
                "guitarist",
                "instrumentalist",
                "producer",
            ],
        },

        "genre_style": {
            "description": "Genre or musical style supported by profile/media evidence.",
            "examples": [
                "acoustic",
                "indie",
                "pop",
                "electronic",
                "folk",
                "rock",
            ],
        },

        "instrumentation": {
            "description": "Instruments demonstrably used by the artist or group.",
            "examples": [
                "acoustic_guitar",
                "electric_guitar",
                "keyboard",
                "percussion",
                "other",
            ],
        },

        "acoustic_electronic": {
            "description": "Whether the demonstrated performance is acoustic, electronic, or hybrid.",
            "examples": [
                "acoustic",
                "electronic",
                "hybrid",
            ],
        },

        "performance_setting": {
            "description": "Performance settings demonstrated by the artist.",
            "examples": [
                "cafe",
                "small_venue",
                "stage",
                "live_event",
                "rehearsal",
                "studio",
            ],
        },

        "energy_profile": {
            "description": "Observable performance energy appropriate to the supplied recordings/media.",
            "examples": [
                "low_background",
                "moderate",
                "lively",
                "high_energy",
                "variable",
            ],
        },

        "vocal_language": {
            "description": "Languages demonstrably used for vocals.",
            "examples": [
                "hindi",
                "english",
                "hindi_english",
                "other",
            ],
        },

        "ensemble_size": {
            "description": "Number of performers in the demonstrated act when determinable.",
            "type": "integer",
        },

        "performance_evidence": {
            "description": "Observable evidence about live/performance capability.",
            "examples": [
                "live_performance",
                "studio_recording",
                "audience_interaction",
                "continuous_set",
            ],
        },

        "setup_footprint": {
            "description": "Evidence-supported estimate of the physical performance setup.",
            "examples": [
                "minimal",
                "small",
                "moderate",
                "large",
            ],
        },
    },
}


# Video Editor

VIDEO_EDITOR_SCHEMA = {
    "category": "video_editor",

    "capability_dimensions": {
        "content_domains": {
            "description": "Content types demonstrated in the supplied editing work.",
            "examples": [
                "food",
                "social",
                "creator",
                "events",
                "interviews",
                "corporate",
                "travel",
                "wedding",
                "hospitality",
                "commercial",
            ],
        },

        "editing_format": {
            "description": "Video formats and editing contexts demonstrated.",
            "examples": [
                "short_form",
                "long_form",
                "vertical_9_16",
                "horizontal",
                "social",
                "reel",
            ],
        },

        "storytelling": {
            "description": "Observable ability to construct a coherent story from footage.",
            "examples": [
                "narrative_sequencing",
                "clip_selection",
                "event_storytelling",
                "interview_structure",
                "visual_continuity",
            ],
        },

        "pacing": {
            "description": "Observable pacing and rhythm of edits.",
            "examples": [
                "slow",
                "moderate",
                "fast",
                "energetic",
                "music_led",
                "narrative_led",
                "variable",
            ],
        },

        "transitions": {
            "description": "Types and degree of transition treatment demonstrated.",
            "examples": [
                "simple_cuts",
                "match_cuts",
                "dissolves",
                "stylized_transitions",
                "minimal_transitions",
                "heavy_transition_use",
            ],
        },

        "captions": {
            "description": "Text/caption treatment demonstrated in the editing work.",
            "examples": [
                "spoken_word_captions",
                "social_captions",
                "subtitles",
                "kinetic_text",
            ],
        },

        "music_audio": {
            "description": "Observable handling of music and audio.",
            "examples": [
                "music_synchronization",
                "beat_synchronization",
                "dialogue_music_balance",
                "sound_effects",
                "audio_cleanup",
                "music_led_editing",
            ],
        },

        "color_treatment": {
            "description": "Observable color grading or treatment.",
            "examples": [
                "natural",
                "cinematic",
                "high_contrast",
                "warm",
                "cool",
                "stylized",
                "commercial",
            ],
        },

        "motion_graphics": {
            "description": "Motion graphics, titles, animation, or VFX demonstrated.",
            "examples": [
                "titles",
                "animated_text",
                "logo_animation",
                "motion_graphics",
                "vfx",
            ],
        },

        "cinematography": {
            "description": "Observable visual/cinematographic capability where relevant.",
            "examples": [
                "composition",
                "camera_movement",
                "framing",
                "visual_continuity",
            ],
        },

        "sound_design": {
            "description": "Observable sound design beyond basic music placement.",
            "examples": [
                "ambient_sound",
                "sound_effects",
                "dialogue_cleanup",
                "sound_layers",
            ],
        },
    },
}


# Lookup--------------------------------------------------------------------------

CATEGORY_SCHEMAS = {
    "photographer": PHOTOGRAPHER_SCHEMA,
    "musician": MUSICIAN_SCHEMA,
    "video_editor": VIDEO_EDITOR_SCHEMA,
}


def get_schema(category: str) -> dict:
    """
    Return the capability schema for an artist category.
    """
    category = category.lower().strip()

    if category not in CATEGORY_SCHEMAS:
        raise ValueError(
            f"Unknown artist category: {category}. "
            f"Expected one of: {sorted(CATEGORY_SCHEMAS)}"
        )

    return CATEGORY_SCHEMAS[category]