import pymongo
import re

from backend.database import collections

books_collection = collections["Books"]

print("✅ Connected to MongoDB successfully!")

dag_mapping = {
    "fiction": [],
    "religious fiction": ['fiction'],
    "speculative fiction": ["fiction"],
    "sci-fi comedy / comic science fiction": ["science fiction", "comedy", "speculative fiction", "fiction"],
    "historical fantasy": ["fantasy", "historical fiction", "speculative fiction", "fiction"],
    "science fantasy": ["science fiction", "fantasy", "social & political fiction", "speculative fiction", "fiction"],
    "libertarian sci-fi": ["science fantasy", "science fiction", "fantasy", "social & political fiction", "speculative fiction", "fiction"],
    "social sci-fi": ["science fantasy", "science fiction", "fantasy", "social & political fiction", "speculative fiction", "fiction"],
    "children's fantasy": ["children's", "fantasy", "fiction", "speculative fiction"],
    "isekai": ["fantasy", "science fiction", "fiction", "speculative fiction"],
    # Note: "science fantasy" appears twice in your mapping.
    # The second occurrence is merged here:
    "science fantasy": ["fantasy", "science fiction", "fiction", "speculative fiction"],
    "dying earth": ["science fantasy", "fantasy", "science fiction", "fiction", "speculative fiction"],
    "planetary romance": ["science fantasy", "romance", "fantasy", "science fiction", "fiction", "speculative fiction"],
    "sword and planet": ["science fantasy", "fantasy", "science fiction", "fiction", "speculative fiction"],
    "superhero fiction": ["fiction", "speculative fiction", "fantasy", "action & adventure"],
    "romantic fantasy": ["fiction", "speculative fiction", "fantasy", "romance"],
    "gothic fiction": ["fiction", "speculative fiction", "fantasy", "horror"],
    "american gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "southern gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "space gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "suburban gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "tasmanian gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "urban gothic": ["gothic fiction", "fiction", "speculative fiction", "fantasy", "horror"],
    "weird west": ["horror", "fantasy", "western", "fiction", "speculative fiction"],
    "adventure fantasy": ["fantasy", "action & adventure", "fiction", "speculative fiction"],
    "heroic fantasy": ["adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"],
    "lost world": ["adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"],
    "sword-and-sandal": ["adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"],
    "sword-and-sorcery": ["adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"],
    "sword-and-soul": ["adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"],
    "wuxia": {"adventure fantasy", "fantasy", "action & adventure", "fiction", "speculative fiction"},
    "space western": {"science fiction", "western", "speculative fiction", "fiction"},
    "fantasy comedy": {"fantasy", "comedy", "speculative fiction", "fiction"},
    "fantasy": {"fiction", "speculative fiction"},
    "high fantasy": {"fantasy", "fiction", "speculative fiction"},
    "low fantasy": {"fantasy", "fiction", "speculative fiction"},
    "contemporary fantasy": {"fantasy", "fiction", "speculative fiction"},
    "occult detective fiction": {"contemporary fantasy", "fantasy", "fiction", "speculative fiction"},
    "paranormal romance": {"contemporary fantasy", "fantasy", "fiction", "speculative fiction"},
    "urban": {"contemporary fantasy", "fantasy", "fiction", "speculative fiction"},
    "cozy fantasy": {"fantasy", "fiction", "speculative fiction"},
    "dark": {"fantasy", "fiction", "speculative fiction"},
    "fairytale": {"fantasy", "fiction", "speculative fiction"},
    "gaslamp": {"fantasy", "fiction", "speculative fiction"},
    "grimdark": {"fantasy", "fiction", "speculative fiction"},
    "hard fantasy": {"fantasy", "fiction", "speculative fiction"},
    "magical realism": {"fantasy", "fiction", "speculative fiction"},
    "mythic fantasy": {"fantasy", "fiction", "speculative fiction"},
    "supernatural": {"fantasy", "fiction", "speculative fiction"},
    "shemo fiction": {"fantasy", "fiction", "speculative fiction"},
    "science fiction": {"fiction", "speculative fiction"},
    "apocalyptic & post-apocalyptic fiction": {"science fiction", "fiction", "speculative fiction"},
    "christian science fiction": {"science fiction", "fiction", "speculative fiction"},
    "comedy science fiction": {"science fiction", "fiction", "speculative fiction"},
    "dystopian": {"science fiction", "fiction", "speculative fiction"},
    "cyberpunk": {"dystopian", "science fiction", "fiction", "speculative fiction"},
    "biopunk": {"cyberpunk", "dystopian", "science fiction", "fiction", "speculative fiction"},
    "dieselpunk": {"cyberpunk", "dystopian", "science fiction", "fiction", "speculative fiction"},
    "japanese cyberpunk": {"cyberpunk", "dystopian", "science fiction", "fiction", "speculative fiction"},
    "nanopunk": {"cyberpunk", "dystopian", "science fiction", "fiction", "speculative fiction"},
    "utopian": {"dystopian", "science fiction", "fiction", "speculative fiction"},
    "feminist science fiction": {"science fiction", "fiction", "speculative fiction"},
    "gothic science fiction": {"science fiction", "fiction", "speculative fiction"},
    "hard science fiction": {"science fiction", "fiction", "speculative fiction"},
    "mecha science fiction": {"science fiction", "fiction", "speculative fiction"},
    "soft science fiction": {"science fiction", "fiction", "speculative fiction"},
    "space science fiction": {"science fiction", "fiction", "speculative fiction"},
    "spy-fi": {"science fiction", "fiction", "speculative fiction"},
    "tech noir": {"science fiction", "fiction", "speculative fiction"},
    "comedy horror": {"comedy", "horror", "fiction"},
    "zombie comedy": {"comedy horror", "comedy", "horror", "fiction"},
    "horror": {"fiction"},
    "body horror": {"horror", "fiction"},
    "ghost stories": {"horror", "fiction"},
    "japanese horror": {"horror", "fiction"},
    "korean horror": {"horror", "fiction"},
    "lovecraftian horror": {"horror", "fiction"},
    "monster literature": {"horror", "fiction"},
    "werewolf fiction": {"monster literature", "horror", "fiction"},
    "vampire literature": {"monster literature", "horror", "fiction"},
    "psychological": {"horror", "fiction"},
    "techno-horror": {"horror", "fiction"},
    "zombie apocalypse": {"horror", "fiction"},
    "historical mystery": {"fiction", "historical fiction", "crime & mystery", "mystery"},
    "alternate history": {"fiction", "historical fiction"},
    "nautical fiction": {"fiction", "historical fiction"},
    "pirate novel": {"fiction", "historical fiction", "nautical fiction"},
    "contemporary fiction": {"fiction"},
    "philosophical fiction": {"fiction"},
    "pop culture": {"fiction"},
    "postmodern": {"fiction"},
    "realist": {"fiction"},
    "hysterical": {"realist", "fiction"},
    "literary fiction": {"fiction"},
    "action & adventure": {"fiction"},
    "theatre fiction": {"fiction"},
    "crime & mystery": {"fiction"},
    "mystery": {"fiction", "crime & mystery"},
    "cozy mystery": {"fiction", "crime & mystery", "mystery"},
    "city mystery": {"fiction", "crime & mystery", "mystery"},
    "detective": {"fiction", "crime & mystery", "mystery"},
    "gong’an": {"fiction", "crime & mystery", "mystery", "detective"},
    "girl detective": {"fiction", "crime & mystery", "mystery", "detective"},
    "police procedural": {"fiction", "crime & mystery", "mystery", "detective"},
    "whodunit": {"fiction", "crime & mystery", "mystery", "detective"},
    "noir": {"fiction", "crime & mystery"},
    "nardic noir": {"fiction", "crime & mystery", "noir"},
    "tart noir": {"fiction", "crime & mystery", "noir"},
    "thriller & suspense": {"fiction"},
    "conspiracy thriller": {"thriller & suspense", "fiction"},
    "erotic thriller": {"thriller & suspense", "fiction"},
    "legal thriller": {"thriller & suspense", "fiction"},
    "financial thriller": {"thriller & suspense", "fiction"},
    "political thriller": {"thriller & suspense", "fiction"},
    "psychological thriller": {"thriller & suspense", "fiction"},
    "techno-thriller": {"thriller & suspense", "fiction"},
    "historical romance": {"fiction", "historical fiction", "romance"},
    "regency romance": {"historical romance", "fiction", "historical fiction", "romance"},
    "romantic suspense": {"fiction", "thriller & suspense", "romance"},
    "western romance": {"fiction", "romance", "western"},
    "romance": {"fiction"},
    "amish romance": {"romance", "fiction"},
    "chivalric romance": {"romance", "fiction"},
    "contemporary romance": {"romance", "fiction"},
    "gay romance": {"contemporary romance", "romance", "fiction"},
    "lesbian romance": {"contemporary romance", "romance", "fiction"},
    "erotic romance": {"romance", "fiction"},
    "inspirational romance": {"romance", "fiction"},
    "paranormal romance": {"romance", "fiction"},
    "time-travel romance": {"paranormal romance", "romance", "fiction"},
    "young adult romance": {"young adult", "romance", "fiction"},
    "women's fiction": {"fiction"},
    "lgbtq+": {"fiction"},
    "graphic novel": {"fiction"},
    "short story": {"fiction"},
    "folklore": {"fiction"},
    "animal tale": {"fiction", "folklore"},
    "fable": {"fiction", "folklore"},
    "fairy tale": {"fiction", "folklore"},
    "ghost story": {"fiction", "folklore"},
    "legend": {"fiction", "folklore"},
    "myth": {"fiction", "folklore"},
    "parable": {"fiction", "folklore"},
    "personal narrative": {"fiction", "folklore"},
    "urban legend": {"fiction", "folklore"},
    "satire": {"fiction"},
    "political thriller": {"fiction", "social & political fiction", "horror & suspense"},
    "western": {"fiction"},
    "northwestern": {"western", "fiction"},
    "action & adventure": {"fiction"},
    "robinsonade fiction": {"action & adventure", "fiction"},
    "nautical fiction": {"action & adventure", "fiction"},
    "pirate fiction": {"action & adventure", "fiction", "nautical fiction"},
    "spy fiction": {"action & adventure", "fiction"},
    "spy-fi": {"action & adventure", "fiction", "spy fiction"},
    "subterranean fiction": {"action & adventure", "fiction"},
    "swashbuckler": {"action & adventure", "fiction"},
    "picaresque": {"swashbuckler", "action & adventure", "fiction"},
    "comedy": {"fiction"},
    "burleque": {"comedy", "fiction"},
    "parody": {"comedy", "fiction"},
    "metaparody": {"parody", "comedy", "fiction"},
    "surreal comedy": {"comedy", "fiction"},
    "tall tale": {"comedy", "fiction"},
    "tragicomedy": {"comedy", "fiction"},
    "nonfiction": [],
    "academic": {"nonfiction"},
    "literature review": {"nonfiction", "academic"},
    "scientific": {"nonfiction", "academic"},
    "technical report": {"nonfiction", "academic"},
    "textbook": {"nonfiction", "academic"},
    "thesis": {"nonfiction", "academic"},
    "memoir & autobiography": {"nonfiction"},
    "memoir": {"nonfiction", "memoir & autobiography"},
    "autobiography": {"nonfiction", "memoir & autobiography"},
    "biography": {"nonfiction"},
    "journalistic writing": {"biography", "nonfiction"},
    "arts journalism": {"biography", "nonfiction"},
    "business journalism": {"biography", "nonfiction"},
    "data-driven journalism": {"biography", "nonfiction"},
    "entertainment journalism": {"biography", "nonfiction"},
    "environmental journalism": {"biography", "nonfiction"},
    "fashion journalism": {"biography", "nonfiction"},
    "global journalism": {"biography", "nonfiction"},
    "medical journalism": {"biography", "nonfiction"},
    "political journalism": {"biography", "nonfiction"},
    "science journalism": {"biography", "nonfiction"},
    "sports journalism": {"biography", "nonfiction"},
    "technical journalism": {"biography", "nonfiction"},
    "trade journalism": {"biography", "nonfiction"},
    "video games journalism": {"biography", "nonfiction"},
    "world journalism": {"biography", "nonfiction"},
    "food & drink": {"nonfiction"},
    "cookbook": {"food & drink", "nonfiction"},
    "art & photography": {"nonfiction"},
    "self-help": {"nonfiction"},
    "history": {"nonfiction"},
    "travel": {"nonfiction"},
    "guide book": {"travel", "nonfiction"},
    "travel blog": {"travel", "nonfiction"},
    "true crime": {"nonfiction"},
    "reference work": {"nonfiction"},
    "dictionary": {"reference work", "nonfiction"},
    "thesaurus": {"reference work", "nonfiction"},
    "encyclopedia": {"reference work", "nonfiction"},
    "almanac": {"reference work", "nonfiction"},
    "atlas": {"reference work", "nonfiction"},
    "essay": {"nonfiction"},
    "position paper": {"nonfiction"},
    "guide/how-to": {"nonfiction"},
    "religion & spirituality": {"nonfiction"},
    "christian": {"religion & spirituality", "nonfiction"},
    "islamic": {"religion & spirituality", "nonfiction"},
    "theological": {"religion & spirituality", "nonfiction"},
    "visionary": {"religion & spirituality", "nonfiction"},
    "humanities & social sciences": {"nonfiction"},
    "parenting & families": {"nonfiction"},
    "science & technology": {"nonfiction"},
    "nonfiction children's": {"nonfiction"}
}

genre_hierarchy = { 
    "New Adult": {},
    "Young Adult": {},
    "Lad Lit": {},
    "Fratire": {},
    "Religious Fiction": {},
    "Fiction": {
        "Children's": {
            "Children's Fiction": {}
        },
        "Young Adult Fiction": {},
        "Speculative Fiction": {
            "Science Fiction": {
                "Western": {
                    "Space Western": {}
                },
                "Comedy": {
                    "Sci-Fi Comedy / Comic Science Fiction": {}
                },
                "Fantasy": {
                    "Social & Political Fiction": {
                        "Science Fantasy": {
                            "Libertarian Sci-Fi": {},
                            "Social Sci-Fi": {}
                        }
                    }
                },
                "Fantasy" : {
                    "Isekai": {},
                    "Science Fantasy": {
                        "Dying Earth": {},
                        "Planetary Romance": {},
                        "Sword and Planet": {}
                    },
                },
                "Apocalyptic & Post-Apocalyptic Fiction": {},
                "Christian Science Fiction": {},
                "Dystopian": {
                    "Cyberpunk": {
                        "Biopunk": {},
                        "Dieselpunk": {},
                        "Japanese Cyberpunk": {},
                        "Nanopunk": {}
                    },
                    "Utopian": {}
                },
                "Feminist Science Fiction": {},
                "Gothic Science Fiction": {},
                "Hard Science Fiction": {},
                "Mecha Science Fiction": {},
                "Soft Science Fiction": {},
                "Spy-Fi": {},
                "Tech Noir": {}
            },
            "Fantasy": {
                "Horror": {
                    "Western": {
                        "Weird West": {}
                    }
                },
                "Comedy": {
                    "Fantasy Comedy": {}
                },
                "Action & Adventure": {
                    "Superhero Fiction": {},
                    "Adventure Fantasy": {
                        "Heroic Fantasy": {},
                        "Lost World": {},
                        "Sword-and-Sandal": {},
                        "Sword-and-Sorcery": {},
                        "Sword-and-Soul": {},
                        "Wuxia": {}
                    },
                },
                "Historical Fiction": {
                    "Historical Fantasy": {}
                },
                "Children's": {
                    "Children's Fantasy": {}
                },
                "Romance": {
                    "Romantic Fantasy": {}
                },
                "Horror": {
                    "Gothic Fiction": {
                        "American Gothic": {},
                        "Southern Gothic": {},
                        "Space Gothic": {},
                        "Suburban Gothic": {},
                        "Tasmanian Gothic": {},
                        "Urban Gothic": {}
                    }
                }, 
                "High Fantasy": {},
                "Low Fantasy": {},
                "Contemporary Fantasy": {
                    "Occult Detective Fiction": {},
                    "Paranormal Romance": {},
                    "Urban": {}
                },
                "Cozy Fantasy": {},
                "Dark Fantasy": {},
                "Fairytale": {},
                "Gaslamp Fantasy": {},
                "Grimdark": {},
                "Hard Fantasy": {},
                "Magical Realism": {},
                "Mythic Fantasy": {},
                "Supernatural Fiction": {},
                "Shemo Fiction": {}
            },
            "Horror": {
                "Comedy": {
                    "Comedy Horror": {
                        "Zombie Comedy": {}
                    }
                },
                "Body Horror": {},
                "Ghost Stories": {},
                "Japanese Horror": {},
                "Korean Horror": {},
                "Lovecraftian Horror": {},
                "Monster Literature": {
                    "Werewolf Fiction": {},
                    "Vampire Literature": {}
                },
                "Psychological Horror": {},
                "Techno-Horror": {},
                "Zombie Apocalypse": {}
            }
        },
        "Historical Fiction": {
            "Crime & Mystery": {
                "Mystery": {
                    "Historical Mystery": {}
                }
            },
            "Alternate History": {},
            "Nautical Fiction": {
                "Pirate Novel": {}
            }
        },
        "Contemporary Fiction": {},
        "Philosophical Fiction": {},
        "Pop Culture": {},
        "Postmodern": {},
        "Realist": {
            "Hysterical": {}
        },
        "Literary Fiction": {},
        "Action & Adventure": {},
        "Theatre Fiction": {},
        "Crime & Mystery": {
            "Mystery": {
                "Cozy Mystery": {},
                "City Mystery": {},
                "Detective Fiction": {
                    "Gong'an": {},
                    "Girl Detective": {},
                    "Police Procedural": {},
                    "Whodunit": {}
                },
            },
            "Noir": {
                "Nordic Noir": {},
                "Tart Noir": {}
            }
        },
        "Thriller & Suspense": {
            "Conspiracy Thriller": {},
            "Erotic Thriller": {},
            "Legal Thriller": {},
            "Financial Thriller": {},
            "Political Thriller": {},
            "Psychological Thriller": {},
            "Techno-Thriller": {}
        },
        "Romance": {
            "Young Adult": {
                "Young Adult Romance": {}
            },
            "Thriller & Suspense": {
                "Romantic Suspense": {}
            },
            "Historical Romance": {
                "Regency Romance": {}
            },
            "Western": {
                "Western Romance": {}
            },
            "Amish Romance": {},
            "Chivalric Romance": {},
            "Contemporary Romance": {
                "Gay Romance": {},
                "Lesbian Romance": {}
            },
            "Erotic Romance": {},
            "Inspirational Romance": {},
            "Paranormal Romance": {
                "Time-Travel Romance": {}
            },
            "Young Adult Romance": {}
        },
        "Women's Fiction": {},
        "LGBTQ+": {},
        "Graphic Novel": {},
        "Short Story": {},
        "Western": {
            "Northwestern": {}
        },
        "Folklore": {
            "Animal Tale": {},
            "Fable": {},
            "Fairy Tale": {},
            "Ghost Story": {},
            "Legend": {},
            "Myth": {},
            "Parable": {},
            "Personal Narrative": {},
            "Urban Legend": {}
        },
        "Satire": {},
        "Social & Political Fiction": {
            "Political Thriller": {}
        },
        "Action & Adventure": {
            "Robinsonade Fiction": {},
            "Nautical Fiction": {
                "Pirate Fiction": {}
            },
            "Spy Fiction": {
                "Spy-Fi": {}
            },
            "Subterranean Fiction": {},
            "Swashbuckler": {
                "Picaresque": {}
            }
        },
        "Comedy": {
            "Burleque": {},
            "Parody": {
                "Metaparody": {}
            },
            "Surreal Comedy": {},
            "Tall Tale": {},
            "Tragicomedy": {},
        }
    },
    "Nonfiction": {
        "Philosophy & Theory":{
            "Philosophy":{}
        },
        "Academic": {
            "Literature Review": {},
            "Scientific" : {},
            "Technical Report": {},
            "Textbook": {},
            "Thesis": {}
        },
        "Memoir & Autobiography": {
            "Memoir": {},
            "Autobiography": {}
        },
        "Journalistic Writing": {
            "Arts Journalism": {},
            "Business Journalism": {},
            "Data-Driven Journalism": {},
            "Entertainment Journalism": {},
            "Environmental Journalism": {},
            "Fashion Journalism": {},
            "Global Journalism": {},
            "Medical Journalism": {},
            "Political Journalism": {},
            "Science Journalism": {},
            "Sports Journalism": {},
            "Technical Journalism": {},
            "Trade Journalism": {},
            "Video Games Journalism": {},
            "World Journalism": {}
        },
        "Food & Drink": {
            "Cookbook": {}
        },
        "Art & Photography": {},
        "Self-Help": {},
        "History": {},
        "Travel": {
            "Guide Book": {},
            "Travel Blog": {}
        },
        "True Crime": {},
        "Reference Work": {
            "Dictionary": {},
            "Thesaurus": {},
            "Encyclopedia": {},
            "Almanac": {},
            "Atlas": {}

        },
        "Essay": {
            "Position Paper": {}
        },
        "Religion & Spirituality": {
            "Christian": {},
            "Islamic": {},
            "Theological": {},
            "Visionary": {}
        },
        "Humanities & Social Sciences": {},
        "Parenting & Families": {},
        "Science & Technology": {},
        "Nonfiction Children's": {}
    }
}

# Approved genres (flattened) with manually curated related words/phrases.
approved_genre_related = {
    "new adult": {
        "new adult", "new adult fiction", "modern new adult", "contemporary new adult",
        "coming-of-age new adult", "emerging adult", "adult transition", "new adult novels",
        "new adult literature", "young-adult crossover"
    },
    "religious fiction": {
        "religious fiction", "spiritual fiction", "faith-based fiction", "christian fiction", "theological fiction",
        "biblical fiction", "sacred fiction", "inspirational fiction", "divine fiction",
        "religious allegory", "parabolic fiction", "mystical fiction", "esoteric fiction",
        "faith journey", "redemption", "salvation", "spiritual fiction", "christian narrative", "biblical fiction", 
        "spiritual journey", "sacred fiction", "divine fiction", "inspirational fiction",
        "mystical fiction", "religious allegory", "parabolic fiction", "grace", "miracle", "holiness", "heaven"
    },
    "young adult": {
        "young adult", "young adult fiction", "ya fiction", "teen fiction", "adolescent",
        "coming-of-age", "youth literature", "ya novels", "young adult narratives", "teen stories"
    },
    "lad lit": {
        "lad lit", "boy lit", "male humor", "urban lad lit", "cheeky lad lit",
        "witty male fiction", "irreverent boy stories", "lads coming-of-age", "frisky lad lit", "male misadventures"
    },
    "fratire": {
        "fratire", "fraternity fiction", "college satire", "campus comedy", "frat humor",
        "university satire", "Greek life stories", "frat novels", "campus misadventures", "party lit"
    },
    "fiction": {
        "fiction", "narrative fiction", "creative fiction", "imaginative literature",
        "novel writing", "fictional prose", "modern fiction", "literary fiction", "fiction narratives", "fiction writing"
    },
    "children's": {
        "children's", "kids literature", "juvenile", "childrens books", "early readers",
        "kids stories", "child literature", "picture books", "childhood tales", "kid-friendly"
    },
    "children's fiction": {
        "children's fiction", "juvenile fiction", "kids fiction", "storybooks", "child narrative",
        "picture story books", "adventure for kids", "kid narratives", "children’s novels", "child fiction"
    },
    "young adult fiction": {
        "young adult fiction", "ya narrative", "teen novels", "adolescent fiction", "youth storytelling",
        "modern young adult", "emerging teen fiction", "coming-of-age stories", "young-adult prose", "young-adult narratives"
    },
    "speculative fiction": {
        "speculative fiction", "futuristic fiction", "alternative fiction", "visionary fiction",
        "what-if fiction", "imaginative futures", "experimental fiction", "speculative narratives", "alternate reality", "speculative prose"
    },
    "science fiction": {
        "science fiction", "sci-fi", "futuristic", "space opera", "time travel",
        "cyberpunk", "dystopian sci-fi", "tech fiction", "speculative science fiction", "futuristic technology"
        ,"Star Trek"
    },
    "western": {
        "western", "cowboy", "frontier", "old west", "ranch tales",
        "cowboy fiction", "frontier literature", "western novels", "dusty trails", "American frontier"
    },
    "space western": {
        "space western", "cosmic cowboy", "futuristic frontier", "interstellar western", "star cowboy",
        "galactic frontier", "space adventure western", "cosmic western", "sci-fi western", "space outlaws"
    },
    "comedy": {
        "comedy", "satire", "witty", "light-hearted",
        "funny", "comic", "laugh-out-loud", "amusing", "comedic fiction" # "humorous"
    },
    "sci-fi comedy / comic science fiction": {
        "sci-fi comedy", "comic science fiction", "futuristic humor", "space comedy", "absurd sci-fi",
        "intergalactic parody", "geek comedy", "nerd humor", "comic futuristic", "sci-fi parody"
    },
    "fantasy": {
        "fantasy", "magical", "mythical", "epic fantasy", "enchanted",
        "wizardry", "dragon tales", "mythic", "fairytale", "legendary"
    },
    "isekai": {
        "isekai", "alternate world", "portal fantasy", "otherworldly", "parallel world",
        "transported to another world", "world-hopping", "alternate realm", "different world", "isekai adventure"
    },
    "science fantasy": {
        "science fantasy", "hybrid fiction", "futuristic magic", "magic and technology", "techno-magical",
        "sci-fi meets fantasy", "otherworldly science", "fantasy science", "science-inspired magic", "fusion fiction"
    },
    "dying earth": {
        "dying earth", "post-apocalyptic fantasy", "end-of-world", "collapse future", "ruined earth",
        "apocalyptic fantasy", "final days", "last era", "world collapse", "terminal future"
    },
    "planetary romance": {
        "planetary romance", "interplanetary love", "cosmic romance", "space romance", "exotic planet",
        "galactic romance", "futuristic love", "star-crossed romance", "celestial romance", "romance among stars"
    },
    "sword and planet": {
        "sword and planet", "interstellar adventure", "cosmic swordplay", "space epic", "galactic crusade",
        "futuristic chivalry", "heroic space", "sword-wielding adventurers", "interplanetary warriors", "sci-fi sword"
    },
    "apocalyptic & post-apocalyptic fiction": {
        "apocalyptic & post-apocalyptic fiction", "apocalyptic fiction", "post-apocalyptic", "end-times", "afterworld",
        "apocalypse", "world collapse", "ruined earth", "survival fiction", "end-of-world stories"
    },
    "christian science fiction": {
        "christian science fiction", "faith-based sci-fi", "spiritual sci-fi", "biblical sci-fi", "religious futuristic",
        "inspirational sci-fi", "God in the future", "divine science fiction", "sacred sci-fi", "christian futuristic"
    },
    "dystopian": {
        "dystopian", "oppressive future", "bleak fiction", "totalitarian", "grim future",
        "dark dystopia", "authoritarian fiction", "dystopia", "societal collapse", "dystopian society"
    },
    "cyberpunk": {
        "cyberpunk", "neon dystopia", "high-tech low-life", "digital noir", "urban cyber",
        "tech rebellion", "gritty cyberpunk", "cyber revolt", "cyber future", "networked society"
    },
    "biopunk": {
        "biopunk", "genetic dystopia", "bio-engineered", "DNA revolution", "biotech future",
        "mutant fiction", "living technology", "gene splicing", "organic cyberpunk", "biological rebellion"
    },
    "dieselpunk": {
        "dieselpunk", "retro-futuristic", "industrial dystopia", "machine-age", "diesel era",
        "vintage future", "industrial noir", "mechanical future", "old tech fiction", "diesel era fiction"
    },
    "japanese cyberpunk": {
        "japanese cyberpunk", "neon tokyo", "futuristic japan", "cyber samurai", "urban tokyo",
        "tech tokyo", "japanese cyber", "cyber japan", "tokyo dystopia", "futuristic nippon"
    },
    "nanopunk": {
        "nanopunk", "nanotech dystopia", "molecular future", "nano revolution", "microscopic tech",
        "cellular sci-fi", "nano engineered", "miniscule tech", "nanotechnology fiction", "small scale sci-fi"
    },
    "utopian": {
        "utopian", "perfect society", "ideal future", "harmonious world", "visionary society",
        "optimistic fiction", "dream world", "idealistic", "future paradise", "utopia"
    },
    "feminist science fiction": {
        "feminist science fiction", "women's sci-fi", "gender-aware sci-fi", "empowered future", "feminist speculative",
        "female empowerment sci-fi", "progressive sci-fi", "gender equality fiction", "women in sci-fi", "feminist futurism"
    },
    "gothic science fiction": {
        "gothic science fiction", "dark sci-fi", "eerie sci-fi", "haunted technology", "gothic dystopia",
        "spooky sci-fi", "techno-gothic", "shadowy futuristic", "gothic speculative", "futuristic gothic"
    },
    "hard science fiction": {
        "hard science fiction", "rigorous sci-fi", "scientifically grounded", "technical sci-fi", "realistic science fiction",
        "engineering fiction", "theory-based sci-fi", "precise sci-fi", "real science fiction", "hard sf"
    },
    "mecha science fiction": {
        "mecha science fiction", "giant robots", "robotic warriors", "mechanized fiction", "mecha saga",
        "robot battle", "cyber-mech", "mecha adventure", "robotic epic", "mecha warfare"
    },
    "soft science fiction": {
        "soft science fiction", "character-driven sci-fi", "social sci-fi", "interpersonal sci-fi", "gentle sci-fi",
        "humanistic sci-fi", "speculative social fiction", "soft sf", "future society fiction", "thoughtful sci-fi"
    },
    "spy-fi": {
        "spy-fi", "espionage sci-fi", "covert operations", "futuristic spies", "secret agent sci-fi",
        "undercover future", "spy thriller sci-fi", "cyber espionage", "espionage fiction", "spy technology"
    },
    "tech noir": {
        "tech noir", "futuristic noir", "digital detective", "urban cyber noir", "tech-infused mystery",
        "neon noir", "dark tech fiction", "cyber detective", "tech noir thriller", "technological noir"
    },
    "horror": {
        "horror", "terrifying", "nightmare", "chilling", "macabre",
        "gruesome", "spine-tingling", "fear-inducing", "haunting", "bloodcurdling"
    },
    "gothic fiction": {
        "gothic fiction", "gothic", "dark romance", "haunted", "brooding",
        "mysterious", "gloomy", "Victorian gothic", "macabre gothic", "atmospheric gothic"
    },
    "american gothic": {
        "american gothic", "southern gothic", "gothic america", "dark american", "haunted america",
        "American horror", "American gothic novels", "American macabre", "gothic southern", "American dark"
    },
    "southern gothic": {
        "southern gothic", "gothic south", "deep south gothic", "southern horror", "southern decay",
        "gothic americana", "southern mystery", "gothic tradition", "sultry gothic", "rural gothic"
    },
    "space gothic": {
        "space gothic", "cosmic gothic", "interstellar gothic", "galactic horror", "futuristic gothic",
        "space horror", "gothic sci-fi", "cosmic dark", "galactic gothic", "astral gothic"
    },
    "suburban gothic": {
        "suburban gothic", "gothic suburbia", "creepy suburbia", "quiet horror", "suburban dread",
        "banal horror", "suburban decay", "hidden darkness", "urban suburban gothic", "suburban nightmare"
    },
    "tasmanian gothic": {
        "tasmanian gothic", "gothic tasmania", "island gothic", "tasmanian horror", "remote gothic",
        "isolated gothic", "tasmanian dark", "gothic outback", "gothic wilderness", "tasmanian mystery"
    },
    "urban gothic": {
        "urban gothic", "city gothic", "modern gothic", "urban horror", "contemporary gothic",
        "gothic urban", "metropolitan horror", "cityscape gothic", "urban decay gothic", "downtown gothic"
    },
    "fantasy comedy": {
        "fantasy comedy", "comic fantasy", "funny fantasy", "humorous fantasy", "whimsical fantasy",
        "lighthearted fantasy", "comedic magic", "silly fantasy", "joking fantasy", "fantasy humor"
    },
    "action & adventure": {
        "action & adventure", "adventure", "thrilling adventure", "action packed", "exciting journey",
        "heroic adventure", "adrenaline rush", "quest", "epic journey", "action saga"
    },
    "superhero fiction": {
        "superhero fiction", "superheroes", "comic book heroes", "caped crusaders", "heroic action",
        "superpower stories", "vigilante fiction", "urban heroes", "comic superhero", "action hero"
    },
    "adventure fantasy": {
        "adventure fantasy", "epic adventure", "fantasy quest", "heroic fantasy", "mythic adventure",
        "sword and sorcery", "fantasy journey", "legendary adventure", "adventure saga", "quest fantasy"
    },
    "heroic fantasy": {
        "heroic fantasy", "epic heroes", "legendary heroes", "sword and sorcery", "mythic heroes",
        "adventure heroes", "fantasy valor", "heroic quests", "legendary adventure", "epic legends"
    },
    "lost world": {
        "lost world", "hidden civilization", "forgotten lands", "undiscovered world", "lost civilization",
        "ancient world", "unexplored lands", "mysterious world", "exotic world", "lost territory"
    },
    "sword-and-sandal": {
        "sword-and-sandal", "sword and sandal", "ancient adventure", "classical epic", "roman epic",
        "greek adventure", "historical adventure", "mythic adventure", "sword and glory", "ancient warriors"
    },
    "sword-and-sorcery": {
        "sword-and-sorcery", "sword and sorcery", "sorcery", "magic and sword", "fantasy combat",
        "sword magic", "mythical battle", "sword epic", "heroic magic", "sorcerous adventure"
    },
    "sword-and-soul": {
        "sword-and-soul", "sword and soul", "spiritual sword", "soulful battle", "ethereal combat",
        "inner quest", "soul adventure", "sword spirit", "soulful fantasy", "spiritual combat"
    },
    "wuxia": {
        "wuxia", "martial arts", "kung fu", "heroic chivalry", "wuxia novels",
        "martial fantasy", "Chinese martial", "swordsmanship", "wuxia adventure", "martial heroes"
    },
    "historical fiction": {
        "historical fiction", "period piece", "vintage", "past era", "old world",
        "historical novels", "historical narrative", "antique literature", "time period fiction", "period drama"
    },
    "historical fantasy": {
        "historical fantasy", "fantasy history", "period magic", "historical magic", "alternate history fantasy",
        "mythic past", "magical history", "fantastical past", "historical epic fantasy", "time-twisted history"
    },
    "children's fantasy": {
        "children's fantasy", "kids fantasy", "juvenile fantasy", "childhood magic", "imaginative kids",
        "fairytale for kids", "child fantasy", "fantasy for children", "magical kids", "youth fantasy"
    },
    "romance": {
        "romance", "romantic", "love story", "romance fiction", "romantic literature",
        "romantic novels", "heartfelt", "passionate", "love narrative", "romantic tales"
    },
    "romantic fantasy": {
        "romantic fantasy", "fantasy romance", "magical romance", "mythic romance", "enchanted romance",
        "epic romance", "romantic magic", "fantasy love", "otherworldly romance", "romantic adventure"
    },
    "high fantasy": {
        "high fantasy", "epic fantasy", "legendary fantasy", "mythic fantasy", "fantasy epic",
        "grand fantasy", "world-building fantasy", "heroic fantasy", "classic fantasy", "fantasy saga"
    },
    "low fantasy": {
        "low fantasy", "urban fantasy", "realistic fantasy", "everyday magic", "modern fantasy",
        "gritty fantasy", "down-to-earth fantasy", "subtle fantasy", "low key fantasy", "minimal fantasy"
    },
    "contemporary fantasy": {
        "contemporary fantasy", "modern fantasy", "current fantasy", "urban magic", "real-world fantasy",
        "present-day fantasy", "modern myth", "everyday fantasy", "contemporary magical", "modern enchantment"
    },
    "occult detective fiction": {
        "occult detective fiction", "occult detective", "supernatural detective",  "paranormal detective",
        "arcane mystery", "esoteric detective", "occult mystery", "supernatural investigation", "occult sleuth" # "mystic crime",
    },
    "paranormal romance": {
        "paranormal romance", "supernatural romance", "otherworldly romance", "ghost romance", "vampire romance",
        "werewolf romance", "haunted romance", "paranormal love", "romantic paranormal", "occult romance"
    },
    "urban": {
        "urban", "city", "metropolitan", "urban fiction", "contemporary city",
        "city life", "urban stories", "urban narrative", "modern city", "urban culture"
    },
    "cozy mystery": {
        "cozy mystery", "cozy crime", "gentle mystery", "light mystery", "wholesome detective",
        "cozy sleuth", "small town mystery", "non-violent mystery", "friendly mystery", "cozy whodunit"
    },
    "city mystery": {
        "city mystery", "urban mystery", "metropolitan mystery", "city crime", "big city detective",
        "urban whodunit", "urban noir", "city sleuth", "urban investigation", "city detective"
    },
    "detective fiction": {
        "detective fiction",  "crime detective", "sleuth", "private eye", #"detective",
        "investigation fiction", "mystery detective", "detective novel", "detective story", "hardboiled detective"
    },
    "gong'an": {
        "gong'an", "chinese detective", "gong'an fiction", "chinese mystery", "chinese crime",
        "court case fiction", "gong'an detective", "chinese sleuth", "chinese police procedural", "gong'an story"
    },
    "girl detective": {
        "girl detective", "female detective", "women detective", "girl sleuth", "young detective",
        "female sleuth", "girl mystery", "young female detective", "teen detective", "girl investigator"
    },
    "police procedural": {
        "police procedural", "police", "cop fiction", "law enforcement", "detective police",
        "police investigation", "procedural mystery", "police novel", "police drama", "police story"
    },
    "whodunit": {
        "whodunit", "clue-based mystery", "puzzle mystery", "crime puzzle",
        "detective puzzle", "who did it", "clue hunt", "murder mystery", "whodunit novel" #, "mystery"
    },
    "noir": {
        "noir", "film noir", "hardboiled", "dark crime", "shadowy mystery",
        "noir fiction", "gritty crime", "underworld noir", "pulp noir", "noir detective"
    },
    "nordic noir": {
        "nordic noir", "scandinavian noir", "cold noir", "nordic crime", "scandinavian crime",
        "northern noir", "nordic detective", "icy noir", "nordic mystery", "nordic thriller"
    },
    "tart noir": {
        "tart noir", "satirical noir", "acidic noir", "biting noir", "scathing noir",
        "dark satire noir", "tart mystery", "acerbic noir", "tart crime", "tart detective"
    },
    "thriller & suspense": {
        "thriller & suspense", "thriller", "suspense", "edge-of-your-seat", "fast-paced",
        "adrenaline rush", "pulse-pounding", "tense thriller", "suspense fiction", "gripping suspense"
    },
    "conspiracy thriller": {
        "conspiracy thriller", "conspiracy", "secret plots", "government conspiracy", "hidden agenda",
        "shadow government", "thriller conspiracy", "political conspiracy", "underground thriller", "covert thriller"
    },
    "erotic thriller": {
        "erotic thriller", "sexy thriller", "sensual suspense", "erotic suspense", "thriller romance",
        "passionate thriller", "seductive mystery", "racy thriller", "erotic mystery", "steamy thriller"
    },
    "legal thriller": {
        "legal thriller", "law thriller", "courtroom thriller", "legal suspense", "justice thriller",
        "lawyer fiction", "court drama", "legal crime", "attorney thriller", "law and order fiction"
    },
    "financial thriller": {
        "financial thriller", "money thriller", "banking thriller", "corporate crime thriller", "economics thriller",
        "financial suspense", "stock market thriller", "investment thriller", "financial conspiracy", "business thriller"
    },
    "political thriller": {
        "political thriller", "political suspense", "power thriller", "government thriller", "espionage thriller",
        "political intrigue", "state thriller", "diplomatic thriller", "politics and suspense", "political conspiracy"
    },
    "psychological thriller": {
        "psychological thriller", "mind thriller", "mental suspense", "psychological suspense", "brain-teaser thriller",
        "inner conflict thriller", "cerebral thriller", "psych drama", "psychological mystery", "mind-bending thriller"
    },
    "techno-thriller": {
        "techno-thriller", "technology thriller", "high-tech thriller", "cyber thriller", "digital thriller",
        "tech suspense", "electronic thriller", "computer thriller", "tech warfare", "tech-driven thriller"
    },
    "young adult romance": {
        "young adult romance", "ya romance", "teen romance", "young love", "romantic young adult",
        "teen love story", "ya love", "adolescent romance", "young adult love", "romance for teens"
    },
    "romantic suspense": {
        "romantic suspense", "romance thriller", "love and suspense", "passionate thriller", "suspense romance",
        "thrilling romance", "romantic mystery", "romance with suspense", "heart-pounding romance", "romantic danger"
    },
    "historical romance": {
        "historical romance", "period romance", "vintage romance", "antique romance", "old-world romance",
        "historical love", "regency romance", "period love story", "classic romance", "historical passion"
    },
    "regency romance": {
        "regency romance", "regency", "period romance", "historical regency", "regency love",
        "regency era romance", "british regency romance", "regency novels", "regency literature", "regency tales"
    },
    "western romance": {
        "western romance", "cowboy romance", "frontier romance", "ranch romance", "western love",
        "american western romance", "old west romance", "western passion", "dusty romance", "frontier love"
    },
    "amish romance": {
        "amish romance", "amish love", "amish relationship", "traditional amish romance", "amish novels",
        "amish literature", "amish heart", "rural amish romance", "amish coming-of-age", "amish storytelling"
    },
    "chivalric romance": {
        "chivalric romance", "knightly romance", "courtly love", "medieval romance", "chivalry",
        "knight tales", "romantic chivalry", "heroic romance", "medieval love", "chivalric adventure"
    },
    "contemporary romance": {
        "contemporary romance", "modern romance", "current love", "urban romance", "today's romance",
        "modern love story", "contemporary love", "modern relationship", "current romance", "21st century romance"
    },
    "gay romance": {
        "gay romance", "homoromance", "lgbt romance", "gay love", "gay relationship",
        "queer romance", "gay love story", "same-sex romance", "gay narrative", "lgbt love"
    },
    "lesbian romance": {
        "lesbian romance", "lesbian love", "queer romance", "lesbian relationship", "lesbian fiction",
        "same-sex romance", "lesbian love story", "queer love", "lgbt romance", "women's queer romance"
    },
    "erotic romance": {
        "erotic romance", "sexy romance", "sensual romance", "erotic love", "steamy romance",
        "passionate romance", "erotic fiction", "romance with sex", "seductive romance", "intimate romance"
    },
    "inspirational romance": {
        "inspirational romance", "faith-based romance", "uplifting romance", "spiritual romance", "heartwarming romance",
        "inspirational love", "hopeful romance", "motivational romance", "positive romance", "inspirational love story"
    },
    "time-travel romance": {
        "time-travel romance", "temporal romance", "romance across time", "time-hopping romance", "historic romance with time travel",
        "romantic time travel", "time-crossed romance", "chronological romance", "time-bound love", "time-displaced romance"
    },
    "women's fiction": {
        "women's fiction", "female fiction", "women literature", "women narratives", "women's novels",
        "women's stories", "lady fiction", "female perspective", "women's writing", "women's tales"
    },
    "lgbtq+": {
        "lgbtq+", "lgbtq fiction", "queer fiction", "gay and lesbian", "lgbt literature",
        "queer literature", "lgbt stories", "lgbt novels", "diverse romance", "lgbt narrative"
    },
    "graphic novel": {
        "graphic novel", "comics", "illustrated fiction", "visual novel", "comic book",
        "graphic literature", "visual storytelling", "illustrated novel", "comic narrative", "sequential art"
    },
    "short story": {
        "short story", "short fiction", "novelette", "flash fiction", "brief narrative",
        "mini fiction", "short prose", "compact story", "short tale", "short narrative"
    },
    "northwestern": {
        "northwestern", "northwestern fiction", "midwest fiction", "northern fiction", "regional western",
        "northwestern literature", "regional stories", "western region fiction", "midwestern tales", "northern narratives"
    },
    "folklore": {
        "folklore", "folktale", "myth", "legend", "fairy tale",
        "fable", "oral tradition", "mythology", "folk narrative", "traditional tales"
    },
    "Animal Tale": {
        "animal tale", "beast tale", "creature tale", "animal fable", "fabled animal",
        "wildlife tale", "animal story", "tale of animals", "animal narrative", "zoo tale"
    },
    "Fable": {
        "fable", "moral tale", "allegory", "didactic tale", "folktale",
        "fabled story", "moral fable", "lesson tale", "short moral story", "allegorical fable"
    },
    "Fairy Tale": {
        "fairy tale", "fairytale", "enchanted tale", "magical story", "once upon a time",
        "childhood tale", "mythic fairy", "storybook", "fantasy tale", "whimsical tale"
    },
    "Ghost Story": {
        "ghost story", "spectral tale", "haunted narrative", "spooky story", "paranormal tale",
        "phantom tale", "eerie ghost", "haunting story", "ghostly narrative", "supernatural ghost"
    },
    "Legend": {
        "legend", "myth", "folklore", "traditional tale", "heroic legend",
        "urban legend", "saga", "fabled tale", "ancient legend", "epic legend"
    },
    "Myth": {
        "myth", "legend", "folklore", "mythology", "traditional myth",
        "creation myth", "ancient myth", "mythic narrative", "allegorical myth", "mythic story"
    },
    "Parable": {
        "parable", "moral tale", "allegory", "didactic story", "lesson narrative",
        "spiritual parable", "parable narrative", "moral parable", "teaching tale", "illustrative parable"
    },
    "Personal Narrative": {
        "personal narrative", "memoir", "autobiographical story", "life story", "self-narrative",
        "biographical account", "first-person narrative", "confessional writing", "personal essay", "life memoir"
    },
    "Urban Legend": {
        "urban legend", "urban myth", "city legend", "modern folklore", "contemporary legend",
        "street tale", "metropolitan myth", "urban tale", "city myth", "urban narrative"
    },
    "Satire": {
        "satire", "lampoon", "parody", "burlesque", "irony",
        "mockery", "satirical comedy", "caricature", "spoof", "satirical writing"
    },
    "Social & Political Fiction, Horror & Suspense": {
        "social political horror", "political suspense", "social thriller", "political terror",
        "socio-political suspense", "dark social fiction", "political horror", "horror with politics",
        "social commentary horror", "suspenseful political horror"
    },
    "Political Thriller": {
        "political thriller", "political suspense", "government thriller", "espionage thriller", "state thriller",
        "political intrigue", "diplomatic thriller", "power thriller", "political conspiracy", "political crime thriller"
    },
    "Western": {
        "western", "cowboy", "frontier", "old west", "ranch tale",
        "cowboy fiction", "wild west", "outlaw story", "frontier saga", "western adventure"
    },
    "Northwestern": {
        "northwestern", "midwestern", "regional western", "northern fiction", "midwest tale",
        "northwestern literature", "regional narrative", "northern saga", "midwestern story", "north narrative"
    },
    "Action & Adventure": {
        "action & adventure", "adventure", "thrill", "heroic journey", "action-packed",
        "adrenaline adventure", "quest", "expedition", "epic journey", "adventure saga"
    },
    "Robinsonade Fiction": {
        "robinsonade", "shipwreck story", "castaway tale", "desert island fiction", "survival adventure",
        "island narrative", "marooned story", "solitary survival", "stranded tale", "isolation adventure"
    },
    "Nautical Fiction": {
        "nautical fiction", "sea story", "maritime adventure", "sailing tale", "ocean narrative",
        "naval fiction", "ship story", "seafaring", "water adventure", "marine narrative"
    },
    "Pirate Fiction": {
        "pirate fiction", "swashbuckler", "buccaneer", "corsair", "pirate adventure",
        "high seas adventure", "treasure hunt", "roguish tale", "pirate saga", "sea bandit"
    },
    "Spy Fiction": {
        "spy fiction", "espionage", "secret agent", "covert thriller", "undercover fiction",
        "spy novel", "intelligence tale", "espionage narrative", "secret service", "spy narrative"
    },
    "Spy-Fi": {
        "spy-fi", "spy science fiction", "futuristic espionage", "tech spy", "cyber espionage",
        "secret agent sci-fi", "spy futuristic", "spy technology", "high-tech spy", "spy sci-fi"
    },
    "Subterranean Fiction": {
        "subterranean fiction", "underground tale", "cave story", "below-ground fiction", "subsurface adventure",
        "underground narrative", "buried world", "earthbound tale", "cavern fiction", "underworld story"
    },
    "Swashbuckler": {
        "swashbuckler", "swordplay", "dashing hero", "sword-and-sorcery", "romantic adventure",
        "daring escapade", "swashbuckling hero", "high adventure", "swordfight", "action adventure"
    },
    "Picaresque": {
        "picaresque", "rogue narrative", "rascal tale", "mischievous story", "roguish adventure",
        "episodic adventure", "trickster tale", "rascal fiction", "picaresque novel", "cheeky narrative"
    },
    "Comedy": {
        "comedy", "humor", "funny", "satire", "witty",
        "laugh-out-loud", "amusing", "comic", "jovial", "light-hearted"
    },
    "Burleque": {
        "burleque", "burlesque", "ribald humor", "vaudeville", "parodic",
        "lampoon", "comic exaggeration", "risqué humor", "satirical burlesque", "stage parody"
    },
    "Parody": {
        "parody", "spoof", "lampoon", "caricature", "imitation",
        "mockery", "pastiche", "satirical imitation", "burlesque parody", "comic mimicry"
    },
    "Metaparody": {
        "metaparody", "self-referential parody", "meta spoof", "parody of parodies", "ironic parody",
        "postmodern parody", "self-aware parody", "meta satire", "parody commentary", "parody within parody"
    },
    "Surreal Comedy": {
        "surreal comedy", "absurd humor", "bizarre comedy", "non sequitur humor", "dreamlike humor",
        "quirky comedy", "offbeat humor", "surrealistic comedy", "weird comedy", "dadaist humor"
    },
    "Tall Tale": {
        "tall tale", "exaggerated story", "hyperbolic narrative", "whopper", "legendary exaggeration",
        "mythic exaggeration", "yarn", "outlandish story", "overblown tale", "folk exaggeration"
    },
    "Tragicomedy": {
        "tragicomedy", "tragic comedy", "bittersweet drama", "dramedy", "comedy tragedy",
        "melodramatic humor", "sad humor", "tragic humor", "blend of tragedy and comedy", "emotional dramedy"
    },

    # -- Nonfiction Group --
    "Nonfiction": {
        "nonfiction", "non-fiction", "factual literature", "real stories", "documentary writing",
        "true narrative", "actual accounts", "authentic literature", "literary nonfiction", "true stories",
        "psychology", "productivity", ""
    },
    "Academic": {
        "academic", "scholarly", "research", "university", "educational",
        "erudite", "academic writing", "peer-reviewed", "studies", "scholarly work"
    },
    "Literature Review": {
        "literature review", "research review", "scholarly review", "critical review", "academic review",
        "survey of literature", "bibliographic review", "review article", "literary analysis", "textual review"
    },
    "Scientific": {
        "scientific", "research-based", "empirical", "laboratory", "experimental",
        "scientific study", "data-driven", "methodical", "science-based", "evidence-based"
    },
    "Technical Report": {
        "technical report", "technical documentation", "research report", "engineering report", "project report",
        "data report", "operational report", "field report", "technical analysis", "documentation report"
    },
    "Textbook": {
        "textbook", "educational book", "instructional book", "learning manual", "academic text",
        "course book", "study guide", "reference textbook", "curriculum book", "school book"
    },
    "Thesis": {
        "thesis", "dissertation", "research thesis", "graduate thesis", "academic thesis",
        "doctoral thesis", "master's thesis", "scholarly dissertation", "research paper", "final project"
    },
    "Memoir & Autobiography": {
        "memoir & autobiography", "personal memoir", "life memoir", "autobiographical account", "self-written life story",
        "confessional writing", "personal narrative", "life history", "memoir literature", "personal recollection"
    },
    "Memoir": {
        "memoir", "personal memoir", "life story", "autobiographical account", "confessional memoir",
        "reminiscence", "personal recollection", "memoir narrative", "first-person memoir", "life memoir"
    },
    "Autobiography": {
        "autobiography", "self-written biography", "personal biography", "life story", "autobiographical narrative",
        "memoir", "self-portrait in writing", "autobiographical account", "personal history", "first-person account"
    },
    "Biography": {
        "biography", "life story", "biographical account", "profile", "biopic",
        "life history", "personal biography", "biographical narrative", "memoir", "documentary biography"
    },
    "Journalistic Writing": {
        "journalistic writing", "news writing", "reporting", "investigative journalism", "press writing",
        "newspaper writing", "media writing", "journalism", "feature writing", "editorial writing"
    },
    "Arts Journalism": {
        "arts journalism", "culture journalism", "art critique", "creative reporting", "entertainment news",
        "art review", "visual arts journalism", "art media", "arts reporting", "cultural commentary"
    },
    "Business Journalism": {
        "business journalism", "financial reporting", "corporate news", "economic journalism", "market analysis",
        "business news", "financial journalism", "corporate analysis", "business reporting", "commercial journalism"
    },
    "Data-Driven Journalism": {
        "data-driven journalism", "infographics journalism", "quantitative journalism", "statistical reporting", "data journalism",
        "analytical journalism", "research journalism", "numeric journalism", "evidence-based reporting", "data analysis"
    },
    "Entertainment Journalism": {
        "entertainment journalism", "celebrity news", "pop culture reporting", "showbiz journalism", "media entertainment",
        "entertainment news", "film journalism", "music journalism", "TV journalism", "entertainment coverage"
    },
    "Environmental Journalism": {
        "environmental journalism", "green journalism", "eco reporting", "sustainability journalism", "climate reporting",
        "environmental news", "nature journalism", "eco news", "environmental analysis", "planetary reporting"
    },
    "Fashion Journalism": {
        "fashion journalism", "style reporting", "fashion news", "trend reporting", "couture journalism",
        "runway news", "fashion critique", "fashion analysis", "designer reporting", "style journalism"
    },
    "Global Journalism": {
        "global journalism", "international reporting", "world news", "global news", "international journalism",
        "world reporting", "global affairs", "cross-border journalism", "worldwide reporting", "international perspective"
    },
    "Medical Journalism": {
        "medical journalism", "health reporting", "medical news", "healthcare journalism", "clinical reporting",
        "medical analysis", "health science reporting", "medical breakthroughs", "medical updates", "healthcare news"
    },
    "Political Journalism": {
        "political journalism", "political reporting", "government news", "political analysis", "policy reporting",
        "politics", "political commentary", "election reporting", "political critique", "public affairs journalism"
    },
    "Science Journalism": {
        "science journalism", "research reporting", "scientific news", "tech journalism", "science news",
        "scientific reporting", "research analysis", "innovation reporting", "science updates", "discovery journalism"
    },
    "Sports Journalism": {
        "sports journalism", "sports reporting", "athletic news", "game coverage", "sports analysis",
        "sporting events", "athlete profiles", "sports commentary", "game analysis", "sports updates"
    },
    "Technical Journalism": {
        "technical journalism", "tech reporting", "engineering news", "technology journalism", "technical analysis",
        "innovation reporting", "tech insights", "industry reporting", "technical updates", "tech review"
    },
    "Trade Journalism": {
        "trade journalism", "industry news", "market journalism", "commercial reporting", "trade news",
        "business sector reporting", "sector analysis", "industry review", "trade analysis", "market updates"
    },
    "Video Games Journalism": {
        "video games journalism", "gaming news", "game reviews", "esports reporting", "game analysis",
        "gaming culture", "video game reviews", "gaming commentary", "interactive media journalism", "game industry reporting"
    },
    "World Journalism": {
        "world journalism", "international news", "global reporting", "world affairs", "multinational journalism",
        "global perspective", "worldwide news", "international perspective", "global affairs", "world coverage"
    },
    "Food & Drink": {
        "food & drink", "culinary", "gastronomy", "cuisine", "food culture",
        "culinary arts", "eating habits", "dining", "food industry", "beverages"
    },
    "Cookbook": {
        "cookbook", "recipe book", "cooking guide", "culinary book", "kitchen manual",
        "recipe collection", "food recipes", "cookery book", "cooking manual", "culinary recipes"
        ,"cook book"
    },
    "Art & Photography": {
        "art & photography", "visual art", "photography", "fine art", "creative imaging",
        "artistic photography", "photo art", "visual culture", "artistic expression", "image art"
    },
    "Self-Help": {
        "self-help", "personal development", "self improvement", "motivational", "inspirational",
        "life coaching", "self guidance", "empowerment", "self care", "personal growth"
    },
    "History": {
        "history", "historical", "past", "chronicle", "annals",
        "heritage", "timeline", "ancient history", "historical study", "historical narrative"
    },
    "Travel": {
        "journey", "exploration", "wanderlust", "adventure", "road trip", "travelogue", 
        "tour across", "tour through", "travel memoir", "voyage", "cross-country", "traveler", "destination", "backpacking", "sightseeing"
    },
    "Guide Book": {
        "guide book", "travel guide", "tour guide", "manual", "handbook",
        "itinerary", "travel manual", "visitor guide", "touring guide", "explorer guide"
    },
    "Travel Blog": {
        "travel blog", "travelogue", "journey blog", "trip blog", "adventure blog",
        "travel writing", "wanderlust blog", "travel diary", "exploration blog", "blog travel"
    },
    "True Crime": {
        "true crime", "crime documentary", "real crime", "criminal investigation", "nonfiction crime",
        "true crime narrative", "actual crime", "real-life crime", "crime report", "true crime story"
    },
    "Reference Work": {
        "reference work", "reference book", "encyclopedic", "compendium", "manual",
        "handbook", "directory", "resource", "reference guide", "reference manual"
    },
    "Dictionary": {
        "dictionary", "lexicon", "wordbook", "glossary", "vocabulary",
        "terminology", "word reference", "language dictionary", "lexical resource", "word guide"
    },
    "Thesaurus": {
        "thesaurus", "synonym dictionary", "word finder", "lexical resource", "word bank",
        "vocabulary reference", "synonym reference", "word thesaurus", "language resource", "word list"
    },
    "Encyclopedia": {
        "encyclopedia", "encyclopedic", "compendium", "knowledge base", "informational resource",
        "encyclopedic reference", "all-inclusive guide", "comprehensive resource", "reference encyclopedia", "encyclopedic work"
    },
    "Almanac": {
        "almanac", "annual", "yearbook", "calendar", "compendium",
        "data book", "fact book", "statistical almanac", "yearly reference", "annual reference"
    },
    "Atlas": {
        "atlas", "map collection", "geographical guide", "world atlas", "cartographic reference",
        "map book", "geography atlas", "regional atlas", "comprehensive atlas", "atlas of maps"
    },
    "Essay": {
        "essay", "article", "discourse", "written reflection", "personal essay",
        "analytical essay", "academic essay", "expository essay", "literary essay", "critical essay"
    },
    "Position Paper": {
        "position paper", "argumentative essay", "policy paper", "opinion piece", "persuasive essay",
        "statement", "research paper", "position statement", "analytical paper", "persuasive writing"
    },
    "Guide/How-to": {
        "guide", "how-to", "tutorial", "instruction manual", "step-by-step guide",
        "DIY guide", "user guide", "instructional book", "self-help guide", "how-to manual"
    },
    "Religion & Spirituality": {
        "religion & spirituality", "spiritual", "faith", "sacred", "divine",
        "religious", "spirituality", "holiness", "soulful", "spiritual journey",
        'theology', 'spirituality', 'doctrine', 'beliefs', 
        'sermon', "prayer", "prayers", "preaching"
    },
    "Christian": {
        "theology", "spirituality", "doctrine", "sermon", "christian history", "spiritual growth", 
        "christian values", "christian teachings", "christian philosophy", 
        "christian devotional", "religious study", "devotional", 
        "christian literature", "christian ethics"
    },
    "Islamic": {
        "islamic", "islam", "muslim", "quranic", "islamic culture",
        "islamic literature", "muslim faith", "islamic tradition", "muslim narrative", "islamic values"
    },
    "Theological": {
        "theological", "theology", "divine studies", "religious theory", "spiritual studies",
        "systematic theology", "theological discourse", "religious philosophy", "divine wisdom", "theological inquiry"
    },
    "Visionary": {
        "visionary", "futuristic", "prophetic", "inspirational", "avant-garde",
        "visionary literature", "revolutionary", "innovative", "futurist", "forward-thinking"
    },
    "Humanities & Social Sciences": {
        "humanities & social sciences", "humanities", "social sciences", "cultural studies", "sociology",
        "anthropology", "philosophy", "social theory", "human culture", "interdisciplinary studies"
    },
    "Parenting & Families": {
        "parenting & families", "parenting", "child-rearing", "family dynamics",
        "parenthood", "family relationships", "domestic life", "family values", "parental guidance",
        "pregnancy", "pregnancies"
    },
    "Science & Technology": {
        "science & technology", "STEM", "tech", "scientific", "technological",
        "innovation", "research", "engineering", "digital", "future tech",
        "C++", "Java", "Python", "CSS", "HTML", "Coding", "C plus plus",
        "Computer Programming", "Computer programs", "Computer science",
        "Fortran", "JavaScript", "PHP", "Pascal", "SQL", "RUBY", "StarLogo",
        "Unix", "Linux", "computer", "computer program"
    },
    "Nonfiction Children's": {
        "nonfiction children's", "kids nonfiction", "juvenile nonfiction", "children's factual", "childrens real stories",
        "educational nonfiction", "young readers nonfiction", "informative for kids", "nonfiction for children", "children's informative"
    }
}


# --- Utility Functions for Matching and User Interaction ---
def matches_phrase(text, phrase):
    """Return True if 'phrase' appears as a distinct whole word in 'text'."""
    pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None

def aggregate_book_text(book):
    """
    Combine a book's "tags" (list) and its "genre" (string) into one searchable text.
    """
    parts = []
    if "tags" in book and isinstance(book["tags"], list):
        parts.extend(book["tags"])
    if "genre" in book and isinstance(book["genre"], str):
        parts.append(book["genre"])
    return " ".join(parts)

def remove_mixed_fiction_nonfiction(genres, summary, genre, tags):
    """
    Separates genres into fiction, nonfiction, and neutral.
    If both fiction and nonfiction are present, prompt the user to choose which branch to keep,
    then return that branch combined with neutral genres.
    After merging, if the resulting set contains the generic "fiction" or "nonfiction" tag along
    with other, more specific genres, remove the generic tag.
    """

    age_range = {
        "children's", "young adult", "adult", "fratire", "lad lit"
    }

    fiction_set = {
        "fiction", "science fiction", "fantasy", "historical fiction",
        "literary fiction", "thriller", "mystery", "speculative fiction",
        "graphic novel", "children's", "speculative fiction",
        "sci-fi comedy / comic science fiction", "historical fantasy",
        "science fantasy", "libertarian sci-fi", "social sci-fi", 
        "children's fantasy", "isekai",  "dying earth", "planetary romance", 
        "sword and planet", "superhero fiction", "romantic fantasy", 
        "gothic fiction", "american gothic","southern gothic", "space gothic",
        "suburban gothic", "tasmanian gothic","urban gothic","weird west", 
        "adventure fantasy", "heroic fantasy", "lost world", "sword-and-sandal", 
        "sword-and-sorcery", "sword-and-soul", "wuxia", "space western", 
        "fantasy comedy", "fantasy", "high fantasy", "low fantasy",
        "contemporary fantasy", "occult detective fiction", "paranormal romance",
        "urban", "cozy fantasy", "dark", "fairytale", "gaslamp", "grimdark",
        "hard fantasy", "magical realism", "mythic fantasy", "supernatural", 
        "shemo fiction", "science fiction", "apocalyptic & post-apocalyptic fiction",
        "christian science fiction", "comedy science fiction", "dystopian", 
        "cyberpunk", "biopunk",  "dieselpunk", "japanese cyberpunk",
        "nanopunk", "utopian", "feminist science fiction", "gothic science fiction",
        "hard science fiction", "mecha science fiction", "soft science fiction", 
        "space science fiction",  "spy-fi", "tech noir", "comedy horror", "zombie comedy", 
        "horror", "body horror", "ghost stories", "japanese horror",
        "korean horror", "lovecraftian horror", "monster literature", 
        "werewolf fiction", "vampire literature", "psychological", "techno-horror", "zombie apocalypse",
        "historical mystery", "alternate history", "nautical fiction",  "pirate novel", "contemporary fiction",
        "philosophical fiction", "pop culture", "postmodern", "realist", "hysterical",
        "literary fiction", "action & adventure", "theatre fiction", "crime & mystery", "mystery",
        "cozy mystery",  "city mystery",  "detective", "gong'an",  "girl detective", "police procedural",
        "whodunit", "noir", "nardic noir", "tart noir", "thriller & suspense", "conspiracy thriller",
        "erotic thriller", "legal thriller", "financial thriller", "political thriller", "psychological thriller", "techno-thriller",
        "historical romance", "regency romance", "romantic suspense", "western romance", "romance", "amish romance", "chivalric romance",
        "contemporary romance", "gay romance", "lesbian romance", "erotic romance", "inspirational romance",
        "paranormal romance", "time-travel romance", "young adult romance", "women's fiction", "lgbtq+",
        "graphic novel", "short story", "folklore", "animal tale",
        "fable",  "fairy tale", "ghost story", "legend", "myth", "parable", "personal narrative",
        "urban legend", "satire", "political thriller",  "western", "northwestern", "action & adventure",
        "robinsonade fiction",  "nautical fiction", "pirate fiction", "spy fiction", "spy-fi",
        "subterranean fiction", "swashbuckler", "picaresque", "comedy", "burleque",
        "parody", "metaparody", "surreal comedy", "tall tale", "tragicomedy", "children's fiction",
        "young adult fiction", "religious fiction", "detective fiction"
    }

    fiction_set = {tag.lower() for tag in (
        fiction_set
    )}
    
    nonfiction_set = {
        "nonfiction", "academic", "literature review", "scientific",
        "technical report", "textbook", "thesis", "memoir & autobiography",
        "memoir", "autobiography", "biography", "journalistic writing",
        "arts journalism", "business journalism", "data-driven journalism",
        "entertainment journalism", "environmental journalism", "fashion journalism",
        "global journalism", "medical journalism", "political journalism",
        "science journalism", "sports journalism", "technical journalism",
        "trade journalism", "video games journalism", "world journalism",
        "food & drink", "cookbook", "art & photography", "self-help", "history",
        "travel", "guide book", "travel blog", "true crime", "reference work",
        "dictionary", "thesaurus", "encyclopedia", "almanac", "atlas",
        "humor", "essay", "position paper", "guide/how-to",
        "religion & spirituality", "christian", "islamic", "theological", "visionary",
        "humanities & social sciences", "parenting & families", "science & technology",
        "nonfiction children's"
    }

    neutral_genres = {g for g in genres if g.lower() in age_range}
    classified = {g for g in genres if g not in neutral_genres}

    # Determine fiction and nonfiction genres using the global sets.
    fiction_genres = {g for g in classified if g.lower() in fiction_set}
    nonfiction_genres = {g for g in classified if g.lower() in nonfiction_set}
    
    # Identify any genres that couldn't be classified (they will be dropped).
    unclassified = classified - fiction_genres - nonfiction_genres
    if unclassified:
        print("Warning: The following genres are unclassified and will be dropped:", unclassified)
    
    tags_lower = [tag.lower() for tag in tags]
    genre_lower = genre.lower()
    
    # Decide which branch to keep.
    if fiction_genres and not nonfiction_genres:
        chosen_branch = fiction_genres
    elif nonfiction_genres and not fiction_genres:
        chosen_branch = nonfiction_genres
    elif fiction_genres and nonfiction_genres:
        if ('fiction' in tags_lower or 'fiction' in genre_lower) and ('nonfiction' not in tags_lower and 'nonfiction' not in genre_lower and 'non-fiction' not in tags_lower and 'non-fiction' not in genre_lower):
            chosen_branch = fiction_genres
            print("Only fiction-related tags/genres found. Removing nonfiction genres.")
            nonfiction_genres = set()

        # If only nonfiction is found, opt to remove fiction genres and set the branch to nonfiction
        elif ('nonfiction' in tags_lower or 'nonfiction' in genre_lower) and ('fiction' not in tags_lower and 'fiction' not in genre_lower):
            chosen_branch = nonfiction_genres
            print("Only nonfiction-related tags/genres found. Removing fiction genres.")
            fiction_genres = set()
        else:
            print(f"Summary: {summary}\n")
            print("Mixed fiction and nonfiction detected.")
            print("Fiction genres found:", fiction_genres)
            print("Nonfiction genres found:", nonfiction_genres)
            choice = input("Keep (F)iction or (N)onfiction? ").strip().lower()
            if choice == "n":
                chosen_branch = nonfiction_genres
            else:
                chosen_branch = fiction_genres
    else:
        chosen_branch = set()

    # Return the chosen branch combined with neutral genres.
    return chosen_branch | neutral_genres

def process_books():
    # Retrieve books where 'genre_tags' does not exist or is an empty list.
    books = list(books_collection.find({
        "$or": [
            {"genre_tags": {"$exists": False}},
            {"genre_tags": {"$size": 0}}
        ]
    }))

    for book in books:
        text = aggregate_book_text(book)
        matched_genres = set()
        
        # Check each approved genre (from approved_genre_related) against the book's text.
        for genre, phrases in approved_genre_related.items():
            for phrase in phrases:
                if matches_phrase(text, phrase):
                    matched_genres.add(genre.lower())
                    break  # Prevent duplicate checks

        title = book.get("title", "Untitled")
        author = book.get("author", "Unknown Author")
        summary = book.get("summary", "No summary available.")
        genre = book.get("genre", "")
        tags = book.get("tags", [])
        current_tags = {tag.lower() for tag in book.get("genre_tags", [])} if book.get("genre_tags") else set()

        print(f"\nBook: {title}")
        print(f"Author: {author}")
        print("Current genre_tags:", current_tags)
        print("Matched Approved Genres:", matched_genres)

        if matched_genres:
            # Extend final genres with parent genres using dag_mapping.
            extended_genres = set(matched_genres)
            for genre in matched_genres:
                if genre in dag_mapping:
                    extended_genres |= set(dag_mapping[genre])

            extended_genres = remove_mixed_fiction_nonfiction(extended_genres, summary, genre, tags)
            new_tags = list(current_tags | extended_genres)

            if new_tags:
                books_collection.update_one(
                    {"_id": book["_id"]},
                    {"$set": {"genre_tags": new_tags}}
                )
                print("Book updated with new genre_tags:", new_tags)
            else:
                print("No new genre_tags to add. Skipping update.")
        else:
            print("No genre_tags detected for addition.")

# call the function
process_books()