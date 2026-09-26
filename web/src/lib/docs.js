// Documentation par type de fiche : à quoi ça sert, quand l'utiliser, champs, utilisation.
// Français et anglais ; les autres langues affichent le français.
export const DOCS = {
  fr: {
    context: {
      what: "Un contexte est un ensemble d'instructions et d'exemples que l'on donne au modèle IA avant la question de l'utilisateur. Il oriente sa réponse sans rien réentraîner : c'est l'in-context learning.",
      when: ["Obtenir des réponses dans un format précis (JSON, tableau, ton de marque).", "Apprendre une tâche au modèle avec quelques exemples (few-shot).", "Donner au modèle des connaissances à jour ou internes à votre entreprise."],
      fields: [["Type", "Few-shot (exemples), instruction système, connaissances ou persona."], ["Instruction système", "Le rôle et les règles du modèle."], ["Exemples", "Paires entrée / sortie attendue, 2 à 10 suffisent souvent."], ["Connaissances", "Texte de référence que le modèle doit utiliser."], ["Modèle cible", "Général, ou une famille et un modèle précis si le contexte a été réglé pour lui."]],
      use: "Onglet « Utiliser » : copiez le JSON et injectez les messages avant la question de l'utilisateur. Un exemple Python avec l'API Anthropic est fourni.",
    },
    prompt: {
      what: "Un prompt est un modèle de texte réutilisable, avec des variables entre doubles accolades, par exemple {{produit}}. On remplace les variables puis on l'envoie au modèle.",
      when: ["Standardiser une demande répétée (résumé, traduction, classement).", "Partager une formulation qui marche bien avec son équipe."],
      fields: [["Gabarit", "Le texte du prompt avec ses variables {{nom}}."], ["Variables", "Détectées automatiquement dans le gabarit."], ["Modèle cible", "Général, ou le modèle pour lequel le prompt a été écrit."]],
      use: "Onglet « Utiliser » : téléchargez le JSON ; l'exemple Python montre comment remplacer les variables.",
    },
    dataset: {
      what: "Un dataset est un jeu d'exemples au format JSONL (une ligne JSON par exemple) qui sert à entraîner ou évaluer un modèle.",
      when: ["Fine-tuner un modèle sur votre domaine (avec une config LoRA).", "Évaluer un modèle sur des cas concrets."],
      fields: [["Format", "Chat (messages), instruction (instruction / réponse) ou complétion ; détecté automatiquement."], ["Contenu", "Collé ou importé ; les gros fichiers partent sur le stockage objet."], ["Aperçu", "Les premières lignes sont affichées sur la fiche."]],
      use: "Onglet « Utiliser » : téléchargez le JSONL, puis chargez-le avec la bibliothèque datasets (exemple fourni) ou directement dans Axolotl.",
    },
    lora: {
      what: "LoRA est une technique pour adapter un modèle existant à une tâche sans le réentraîner entièrement : on entraîne de petits adaptateurs. Une fiche LoRA regroupe tous les réglages de cet entraînement.",
      when: ["Reproduire un fine-tuning qui a fonctionné.", "Partir d'une base éprouvée pour votre propre entraînement."],
      fields: [["Méthode", "LoRA, ou QLoRA (modèle compressé en 4 bits, moins de mémoire)."], ["Modèle de base", "Le modèle à adapter, par exemple Qwen/Qwen2.5-7B-Instruct."], ["Rang, alpha, dropout", "La taille et la force des adaptateurs."], ["Taux d'apprentissage, époques, batch", "Les réglages de l'entraînement."], ["Dataset lié", "Le dataset du catalogue utilisé pour l'entraînement."]],
      use: "Onglet « Utiliser » : téléchargez la config YAML pour Axolotl, ou copiez l'exemple PEFT en Python.",
    },
    tool: {
      what: "Un serveur MCP (Model Context Protocol) donne de nouvelles capacités à un assistant IA : lire des fichiers, interroger une base, appeler un service. Le même serveur fonctionne avec Claude, Cursor et d'autres assistants.",
      when: ["Connecter un assistant à vos outils ou à vos données.", "Partager un serveur que vous avez développé."],
      fields: [["Nom du serveur", "Identifiant court, lettres, chiffres, _ et -."], ["Transport", "stdio (lancé par une commande sur votre machine) ou HTTP (serveur distant)."], ["Commande ou URL", "Comment démarrer ou joindre le serveur."], ["Variables d'environnement", "Les clés à renseigner (noms seulement, jamais les valeurs)."]],
      use: "Onglet « Utiliser » : copiez la commande claude mcp add pour Claude Code, ou le bloc mcpServers pour Claude Desktop et Cursor.",
    },
    model: {
      what: "Un modèle est un modèle IA publié par un Lab vérifié : fine-tune, fusion (merge) ou version quantifiée. La fiche décrit le modèle et renvoie vers son téléchargement.",
      when: ["Trouver un modèle adapté à une tâche ou à votre matériel.", "Publier le modèle que votre Lab a entraîné (statut Lab requis)."],
      fields: [["Type", "Fine-tune, merge, quantifié ou modèle de base."], ["Modèle de base, famille, taille", "D'où vient le modèle et combien de paramètres il a."], ["Format et quantification", "safetensors, GGUF… et niveau de compression."], ["Entraînement", "Datasets et config LoRA utilisés, époques, date."], ["Matériel requis", "VRAM minimale, fonctionnement sur CPU, vitesse."], ["Usage et évaluations", "Langues, cas d'usage, limites, benchmarks, versions."]],
      use: "Bouton « Télécharger le modèle », puis onglet « Utiliser » pour les commandes llama.cpp, Ollama ou Transformers.",
    },
    agent: {
      what: "Un agent est un assistant IA qui enchaîne des étapes pour accomplir une tâche : il suit des instructions, utilise des serveurs MCP et des contextes, et respecte des garde-fous.",
      when: ["Automatiser une tâche en plusieurs étapes (support, veille, tri de documents).", "Partager un agent qui fonctionne, prêt à relancer."],
      fields: [["Instructions", "Le rôle et les règles de l'agent."], ["Étapes", "Le déroulé attendu, une étape par ligne."], ["Framework", "Claude Agent SDK, LangGraph, CrewAI…"], ["Serveurs MCP et contextes", "Les ressources du catalogue que l'agent utilise."], ["Garde-fous", "Ce que l'agent ne doit jamais faire."]],
      use: "Onglet « Utiliser » : téléchargez le JSON de l'agent ; l'exemple Python le lance avec l'API Anthropic.",
    },
    skill: {
      what: "Un skill est un paquet d'instructions (fichier SKILL.md) qu'un assistant comme Claude charge uniquement quand la tâche le demande. Il lui apprend une façon de faire précise.",
      when: ["Donner à l'assistant une méthode maison (compte rendu, relecture, rapport).", "Éviter de répéter les mêmes consignes à chaque conversation."],
      fields: [["Nom du skill", "Identifiant court, minuscules et tirets."], ["Quand l'utiliser", "La phrase qui permet à l'assistant de savoir quand charger le skill."], ["Instructions", "Le contenu du SKILL.md, en Markdown."], ["Fichiers et ressources", "Scripts ou modèles de documents associés (facultatif)."]],
      use: "Téléchargez le SKILL.md et placez-le dans ~/.claude/skills/<nom>/ (ou .claude/skills/ dans un projet).",
    },
    eval: {
      what: "Une évaluation est un jeu de cas de test (entrée et réponse attendue) avec une méthode de notation. Elle mesure si un modèle, un prompt, un contexte ou un agent fait bien son travail.",
      when: ["Comparer deux prompts ou deux modèles sur les mêmes cas.", "Vérifier qu'une modification n'a rien cassé."],
      fields: [["Ressource évaluée", "La fiche du catalogue testée (facultatif)."], ["Méthode de notation", "Contient, exacte, expression régulière ou notée par un modèle."], ["Seuil de réussite", "Le pourcentage de cas réussis à atteindre."], ["Cas de test", "Les entrées et les réponses attendues."]],
      use: "Onglet « Utiliser » : téléchargez le JSONL des cas ; l'exemple Python calcule le score.",
    },
    rag: {
      what: "Un pipeline RAG (génération augmentée par la recherche) permet à un modèle de répondre à partir de vos documents : on les découpe, on les vectorise, puis à chaque question on retrouve les extraits utiles et on les donne au modèle.",
      when: ["Faire répondre un assistant sur une documentation interne ou un catalogue produit.", "Réduire les inventions du modèle en l'obligeant à citer ses sources."],
      fields: [["Sources", "Les documents utilisés et leur mise à jour."], ["Découpage", "Taille et chevauchement des morceaux de texte."], ["Embeddings et base vectorielle", "Le modèle qui vectorise et l'endroit où les vecteurs sont stockés."], ["Recherche", "Nombre d'extraits retenus et reclassement éventuel."], ["Gabarit du prompt", "Le texte envoyé au modèle, avec {{context}} et {{question}}."]],
      use: "Onglet « Utiliser » : téléchargez la configuration JSON ; l'exemple Python décrit chaque étape.",
    },
    harness: {
      what: "Un harness est l'environnement qui fait tourner un agent : son fichier d'instructions (par exemple CLAUDE.md), les outils qu'il a le droit d'utiliser, ce qui lui est interdit, les hooks et les serveurs MCP branchés.",
      when: ["Partager une configuration d'équipe pour Claude Code ou un autre assistant.", "Encadrer un agent : commandes autorisées, fichiers protégés."],
      fields: [["Harness", "Claude Code, Claude Agent SDK, Cursor…"], ["Instructions", "Le fichier de consignes lu par l'agent."], ["Autorisé / interdit", "Les permissions, une règle par ligne."], ["Hooks", "Les actions déclenchées automatiquement (JSON)."], ["Serveurs MCP", "Les serveurs du catalogue à brancher."]],
      use: "Onglet « Utiliser » : copiez le CLAUDE.md et le .claude/settings.json dans votre projet.",
    },
  },
  en: {
    context: {
      what: "A context is a set of instructions and examples given to the AI model before the user's question. It steers the answer without retraining anything: this is in-context learning.",
      when: ["Get answers in a precise format (JSON, table, brand tone).", "Teach the model a task with a few examples (few-shot).", "Give the model up-to-date or company-specific knowledge."],
      fields: [["Type", "Few-shot (examples), system instruction, knowledge or persona."], ["System instruction", "The model's role and rules."], ["Examples", "Input / expected output pairs; 2 to 10 are often enough."], ["Knowledge", "Reference text the model must use."], ["Target model", "General, or a family and specific model it was tuned for."]],
      use: "“Use” tab: copy the JSON and inject the messages before the user's question. A Python example with the Anthropic API is provided.",
    },
    prompt: {
      what: "A prompt is a reusable text template with variables in double braces, for example {{product}}. Fill in the variables, then send it to the model.",
      when: ["Standardize a recurring request (summary, translation, classification).", "Share a wording that works well with your team."],
      fields: [["Template", "The prompt text with its {{name}} variables."], ["Variables", "Detected automatically in the template."], ["Target model", "General, or the model the prompt was written for."]],
      use: "“Use” tab: download the JSON; the Python example shows how to fill the variables.",
    },
    dataset: {
      what: "A dataset is a set of examples in JSONL format (one JSON line per example) used to train or evaluate a model.",
      when: ["Fine-tune a model on your domain (with a LoRA config).", "Evaluate a model on real cases."],
      fields: [["Format", "Chat (messages), instruction or completion; detected automatically."], ["Content", "Pasted or imported; large files go to object storage."], ["Preview", "The first rows are shown on the page."]],
      use: "“Use” tab: download the JSONL and load it with the datasets library (example provided) or directly in Axolotl.",
    },
    lora: {
      what: "LoRA adapts an existing model to a task without fully retraining it: only small adapters are trained. A LoRA page gathers all the settings of that training.",
      when: ["Reproduce a fine-tuning that worked.", "Start your own training from proven settings."],
      fields: [["Method", "LoRA, or QLoRA (4-bit compressed model, less memory)."], ["Base model", "The model to adapt, e.g. Qwen/Qwen2.5-7B-Instruct."], ["Rank, alpha, dropout", "Size and strength of the adapters."], ["Learning rate, epochs, batch", "Training settings."], ["Linked dataset", "The catalog dataset used for training."]],
      use: "“Use” tab: download the YAML config for Axolotl, or copy the PEFT Python example.",
    },
    tool: {
      what: "An MCP (Model Context Protocol) server gives an AI assistant new abilities: read files, query a database, call a service. The same server works with Claude, Cursor and other assistants.",
      when: ["Connect an assistant to your tools or data.", "Share a server you built."],
      fields: [["Server name", "Short identifier: letters, digits, _ and -."], ["Transport", "stdio (started by a command on your machine) or HTTP (remote server)."], ["Command or URL", "How to start or reach the server."], ["Environment variables", "Keys to provide (names only, never values)."]],
      use: "“Use” tab: copy the claude mcp add command for Claude Code, or the mcpServers block for Claude Desktop and Cursor.",
    },
    model: {
      what: "A model is an AI model published by a verified Lab: fine-tune, merge or quantized version. The page describes the model and links to its download.",
      when: ["Find a model suited to a task or your hardware.", "Publish the model your Lab trained (Lab status required)."],
      fields: [["Type", "Fine-tune, merge, quantized or base model."], ["Base model, family, size", "Where the model comes from and how many parameters it has."], ["Format and quantization", "safetensors, GGUF… and compression level."], ["Training", "Datasets and LoRA config used, epochs, date."], ["Hardware", "Minimum VRAM, CPU support, speed."], ["Usage and evaluations", "Languages, use cases, limits, benchmarks, versions."]],
      use: "“Download the model” button, then the “Use” tab for llama.cpp, Ollama or Transformers commands.",
    },
    agent: {
      what: "An agent is an AI assistant that chains steps to complete a task: it follows instructions, uses MCP servers and contexts, and respects guardrails.",
      when: ["Automate a multi-step task (support, monitoring, document triage).", "Share a working agent, ready to rerun."],
      fields: [["Instructions", "The agent's role and rules."], ["Steps", "The expected flow, one step per line."], ["Framework", "Claude Agent SDK, LangGraph, CrewAI…"], ["MCP servers and contexts", "Catalog resources the agent uses."], ["Guardrails", "What the agent must never do."]],
      use: "“Use” tab: download the agent JSON; the Python example runs it with the Anthropic API.",
    },
    skill: {
      what: "A skill is an instruction pack (SKILL.md file) that an assistant like Claude loads only when the task calls for it. It teaches a precise way of doing things.",
      when: ["Give the assistant an in-house method (minutes, review, report).", "Stop repeating the same instructions in every conversation."],
      fields: [["Skill name", "Short identifier, lowercase and dashes."], ["When to use it", "The sentence that tells the assistant when to load the skill."], ["Instructions", "The SKILL.md content, in Markdown."], ["Files and resources", "Related scripts or templates (optional)."]],
      use: "Download SKILL.md and place it in ~/.claude/skills/<name>/ (or .claude/skills/ in a project).",
    },
    eval: {
      what: "An evaluation is a set of test cases (input and expected answer) with a scoring method. It measures whether a model, prompt, context or agent does its job.",
      when: ["Compare two prompts or models on the same cases.", "Check that a change broke nothing."],
      fields: [["Evaluated resource", "The catalog page being tested (optional)."], ["Scoring method", "Contains, exact, regular expression or scored by a model."], ["Pass threshold", "The share of passing cases to reach."], ["Test cases", "Inputs and expected answers."]],
      use: "“Use” tab: download the cases JSONL; the Python example computes the score.",
    },
    rag: {
      what: "A RAG (retrieval-augmented generation) pipeline lets a model answer from your documents: they are chunked and embedded, then for each question the useful excerpts are retrieved and given to the model.",
      when: ["Have an assistant answer from internal docs or a product catalog.", "Reduce hallucinations by making the model cite its sources."],
      fields: [["Sources", "Documents used and how they are updated."], ["Chunking", "Chunk size and overlap."], ["Embeddings and vector store", "The embedding model and where vectors are stored."], ["Retrieval", "Number of excerpts kept and optional reranking."], ["Prompt template", "The text sent to the model, with {{context}} and {{question}}."]],
      use: "“Use” tab: download the JSON config; the Python example describes each step.",
    },
    harness: {
      what: "A harness is the environment that runs an agent: its instructions file (e.g. CLAUDE.md), the tools it may use, what is denied, hooks and connected MCP servers.",
      when: ["Share a team configuration for Claude Code or another assistant.", "Constrain an agent: allowed commands, protected files."],
      fields: [["Harness", "Claude Code, Claude Agent SDK, Cursor…"], ["Instructions", "The instructions file the agent reads."], ["Allowed / denied", "Permissions, one rule per line."], ["Hooks", "Automatically triggered actions (JSON)."], ["MCP servers", "Catalog servers to connect."]],
      use: "“Use” tab: copy CLAUDE.md and .claude/settings.json into your project.",
    }
  },
  es: {
    "context": {
      "what": "Un contexto es un conjunto de instrucciones y ejemplos que se dan al modelo de IA antes de la pregunta del usuario. Orienta la respuesta sin reentrenar nada: es el aprendizaje en contexto (in-context learning).",
      "when": [
        "Obtener respuestas en un formato preciso (JSON, tabla, tono de marca).",
        "Enseñar una tarea al modelo con unos pocos ejemplos (few-shot).",
        "Dar al modelo conocimientos actualizados o propios de tu empresa."
      ],
      "fields": [
        [
          "Tipo",
          "Few-shot (ejemplos), instrucción de sistema, conocimiento o persona."
        ],
        [
          "Instrucción de sistema",
          "El rol y las reglas del modelo."
        ],
        [
          "Ejemplos",
          "Pares entrada / salida esperada; de 2 a 10 suelen bastar."
        ],
        [
          "Conocimiento",
          "Texto de referencia que el modelo debe usar."
        ],
        [
          "Modelo objetivo",
          "General, o una familia y un modelo concreto para el que se ajustó."
        ]
      ],
      "use": "Pestaña “Usar”: copia el JSON e inserta los mensajes antes de la pregunta del usuario. Se incluye un ejemplo en Python con la API de Anthropic."
    },
    "prompt": {
      "what": "Un prompt es una plantilla de texto reutilizable con variables entre llaves dobles, por ejemplo {{product}}. Rellena las variables y envíalo al modelo.",
      "when": [
        "Estandarizar una petición recurrente (resumen, traducción, clasificación).",
        "Compartir con tu equipo una redacción que funciona bien."
      ],
      "fields": [
        [
          "Plantilla",
          "El texto del prompt con sus variables {{name}}."
        ],
        [
          "Variables",
          "Se detectan automáticamente en la plantilla."
        ],
        [
          "Modelo objetivo",
          "General, o el modelo para el que se escribió el prompt."
        ]
      ],
      "use": "Pestaña “Usar”: descarga el JSON; el ejemplo en Python muestra cómo rellenar las variables."
    },
    "dataset": {
      "what": "Un dataset es un conjunto de ejemplos en formato JSONL (una línea JSON por ejemplo) que sirve para entrenar o evaluar un modelo.",
      "when": [
        "Hacer fine-tuning de un modelo en tu dominio (con una config LoRA).",
        "Evaluar un modelo con casos reales."
      ],
      "fields": [
        [
          "Formato",
          "Chat (mensajes), instrucción o completion; se detecta automáticamente."
        ],
        [
          "Contenido",
          "Pegado o importado; los archivos grandes van al almacenamiento de objetos."
        ],
        [
          "Vista previa",
          "Las primeras filas se muestran en la página."
        ]
      ],
      "use": "Pestaña “Usar”: descarga el JSONL y cárgalo con la librería datasets (ejemplo incluido) o directamente en Axolotl."
    },
    "lora": {
      "what": "LoRA adapta un modelo existente a una tarea sin reentrenarlo por completo: solo se entrenan pequeños adaptadores. Una página LoRA reúne todos los parámetros de ese entrenamiento.",
      "when": [
        "Reproducir un fine-tuning que funcionó.",
        "Empezar tu propio entrenamiento con parámetros probados."
      ],
      "fields": [
        [
          "Método",
          "LoRA, o QLoRA (modelo comprimido a 4 bits, menos memoria)."
        ],
        [
          "Modelo base",
          "El modelo a adaptar, p. ej. Qwen/Qwen2.5-7B-Instruct."
        ],
        [
          "Rank, alpha, dropout",
          "Tamaño e intensidad de los adaptadores."
        ],
        [
          "Learning rate, epochs, batch",
          "Parámetros de entrenamiento."
        ],
        [
          "Dataset vinculado",
          "El dataset del catálogo usado para el entrenamiento."
        ]
      ],
      "use": "Pestaña “Usar”: descarga la config YAML para Axolotl o copia el ejemplo en Python con PEFT."
    },
    "tool": {
      "what": "Un servidor MCP (Model Context Protocol) da nuevas capacidades a un asistente de IA: leer archivos, consultar una base de datos, llamar a un servicio. El mismo servidor funciona con Claude, Cursor y otros asistentes.",
      "when": [
        "Conectar un asistente a tus herramientas o datos.",
        "Compartir un servidor que has creado."
      ],
      "fields": [
        [
          "Nombre del servidor",
          "Identificador corto: letras, cifras, _ y -."
        ],
        [
          "Transporte",
          "stdio (lo inicia un comando en tu máquina) o HTTP (servidor remoto)."
        ],
        [
          "Comando o URL",
          "Cómo iniciar o acceder al servidor."
        ],
        [
          "Variables de entorno",
          "Claves que debes proporcionar (solo los nombres, nunca los valores)."
        ]
      ],
      "use": "Pestaña “Usar”: copia el comando claude mcp add para Claude Code, o el bloque mcpServers para Claude Desktop y Cursor."
    },
    "model": {
      "what": "Un modelo es un modelo de IA publicado por un Lab verificado: fine-tune, merge o versión cuantizada. La página describe el modelo y enlaza a su descarga.",
      "when": [
        "Encontrar un modelo adecuado para una tarea o para tu hardware.",
        "Publicar el modelo que entrenó tu Lab (requiere estatus de Lab)."
      ],
      "fields": [
        [
          "Tipo",
          "Fine-tune, merge, cuantizado o modelo base."
        ],
        [
          "Modelo base, familia, tamaño",
          "De dónde viene el modelo y cuántos parámetros tiene."
        ],
        [
          "Formato y cuantización",
          "safetensors, GGUF… y nivel de compresión."
        ],
        [
          "Entrenamiento",
          "Datasets y config LoRA usados, epochs, fecha."
        ],
        [
          "Hardware",
          "VRAM mínima, soporte de CPU, velocidad."
        ],
        [
          "Uso y evaluaciones",
          "Idiomas, casos de uso, límites, benchmarks, versiones."
        ]
      ],
      "use": "Botón “Descargar el modelo” y luego la pestaña “Usar” para los comandos de llama.cpp, Ollama o Transformers."
    },
    "agent": {
      "what": "Un agente es un asistente de IA que encadena pasos para completar una tarea: sigue instrucciones, usa servidores MCP y contextos, y respeta límites de seguridad.",
      "when": [
        "Automatizar una tarea de varios pasos (soporte, vigilancia, clasificación de documentos).",
        "Compartir un agente que funciona, listo para volver a ejecutar."
      ],
      "fields": [
        [
          "Instrucciones",
          "El rol y las reglas del agente."
        ],
        [
          "Pasos",
          "El flujo esperado, un paso por línea."
        ],
        [
          "Framework",
          "Claude Agent SDK, LangGraph, CrewAI…"
        ],
        [
          "Servidores MCP y contextos",
          "Recursos del catálogo que usa el agente."
        ],
        [
          "Límites de seguridad",
          "Lo que el agente nunca debe hacer."
        ]
      ],
      "use": "Pestaña “Usar”: descarga el JSON del agente; el ejemplo en Python lo ejecuta con la API de Anthropic."
    },
    "skill": {
      "what": "Una skill es un paquete de instrucciones (archivo SKILL.md) que un asistente como Claude carga solo cuando la tarea lo requiere. Le enseña una forma precisa de hacer las cosas.",
      "when": [
        "Dar al asistente un método interno (actas, revisión, informe).",
        "Dejar de repetir las mismas instrucciones en cada conversación."
      ],
      "fields": [
        [
          "Nombre de la skill",
          "Identificador corto, en minúsculas y con guiones."
        ],
        [
          "Cuándo usarla",
          "La frase que indica al asistente cuándo cargar la skill."
        ],
        [
          "Instrucciones",
          "El contenido de SKILL.md, en Markdown."
        ],
        [
          "Archivos y recursos",
          "Scripts o plantillas relacionados (opcional)."
        ]
      ],
      "use": "Descarga SKILL.md y colócalo en ~/.claude/skills/<name>/ (o en .claude/skills/ dentro de un proyecto)."
    },
    "eval": {
      "what": "Una evaluación es un conjunto de casos de prueba (entrada y respuesta esperada) con un método de puntuación. Mide si un modelo, prompt, contexto o agente hace bien su trabajo.",
      "when": [
        "Comparar dos prompts o modelos con los mismos casos.",
        "Comprobar que un cambio no ha roto nada."
      ],
      "fields": [
        [
          "Recurso evaluado",
          "La página del catálogo que se prueba (opcional)."
        ],
        [
          "Método de puntuación",
          "Contiene, exacta, expresión regular o puntuado por un modelo."
        ],
        [
          "Umbral de aprobación",
          "El porcentaje de casos aprobados que hay que alcanzar."
        ],
        [
          "Casos de prueba",
          "Entradas y respuestas esperadas."
        ]
      ],
      "use": "Pestaña “Usar”: descarga el JSONL de casos; el ejemplo en Python calcula la puntuación."
    },
    "rag": {
      "what": "Un pipeline RAG (generación aumentada por recuperación) permite a un modelo responder a partir de tus documentos: se dividen en fragmentos y se convierten en embeddings; luego, para cada pregunta, se recuperan los extractos útiles y se pasan al modelo.",
      "when": [
        "Hacer que un asistente responda a partir de documentación interna o de un catálogo de productos.",
        "Reducir las alucinaciones haciendo que el modelo cite sus fuentes."
      ],
      "fields": [
        [
          "Fuentes",
          "Documentos usados y cómo se actualizan."
        ],
        [
          "Fragmentación",
          "Tamaño de fragmento y solapamiento."
        ],
        [
          "Embeddings y base vectorial",
          "El modelo de embeddings y dónde se guardan los vectores."
        ],
        [
          "Recuperación",
          "Número de extractos que se conservan y reranking opcional."
        ],
        [
          "Plantilla de prompt",
          "El texto enviado al modelo, con {{context}} y {{question}}."
        ]
      ],
      "use": "Pestaña “Usar”: descarga la config JSON; el ejemplo en Python describe cada paso."
    },
    "harness": {
      "what": "Un harness es el entorno que ejecuta un agente: su archivo de instrucciones (p. ej. CLAUDE.md), las herramientas que puede usar, lo que tiene prohibido, los hooks y los servidores MCP conectados.",
      "when": [
        "Compartir una configuración de equipo para Claude Code u otro asistente.",
        "Restringir un agente: comandos permitidos, archivos protegidos."
      ],
      "fields": [
        [
          "Harness",
          "Claude Code, Claude Agent SDK, Cursor…"
        ],
        [
          "Instrucciones",
          "El archivo de instrucciones que lee el agente."
        ],
        [
          "Permitido / denegado",
          "Permisos, una regla por línea."
        ],
        [
          "Hooks",
          "Acciones que se disparan automáticamente (JSON)."
        ],
        [
          "Servidores MCP",
          "Servidores del catálogo que conectar."
        ]
      ],
      "use": "Pestaña “Usar”: copia CLAUDE.md y .claude/settings.json en tu proyecto."
    }
  },
  de: {
    "context": {
      "what": "Ein Kontext ist eine Reihe von Anweisungen und Beispielen, die das KI-Modell vor der Frage des Nutzers erhält. Er lenkt die Antwort, ohne etwas neu zu trainieren: Das nennt man In-Context-Learning.",
      "when": [
        "Antworten in einem genauen Format erhalten (JSON, Tabelle, Markenton).",
        "Dem Modell mit wenigen Beispielen eine Aufgabe beibringen (Few-Shot).",
        "Dem Modell aktuelles oder firmenspezifisches Wissen geben."
      ],
      "fields": [
        [
          "Typ",
          "Few-Shot (Beispiele), Systemanweisung, Wissen oder Persona."
        ],
        [
          "Systemanweisung",
          "Rolle und Regeln des Modells."
        ],
        [
          "Beispiele",
          "Paare aus Eingabe und erwarteter Ausgabe; 2 bis 10 reichen oft."
        ],
        [
          "Wissen",
          "Referenztext, den das Modell nutzen muss."
        ],
        [
          "Zielmodell",
          "Allgemein, oder eine Familie und ein bestimmtes Modell, für das er abgestimmt wurde."
        ]
      ],
      "use": "Tab „Verwenden“: Kopiere das JSON und füge die Nachrichten vor der Frage des Nutzers ein. Ein Python-Beispiel mit der Anthropic API ist dabei."
    },
    "prompt": {
      "what": "Ein Prompt ist eine wiederverwendbare Textvorlage mit Variablen in doppelten geschweiften Klammern, zum Beispiel {{product}}. Fülle die Variablen aus und sende ihn dann an das Modell.",
      "when": [
        "Eine wiederkehrende Anfrage vereinheitlichen (Zusammenfassung, Übersetzung, Klassifizierung).",
        "Eine gut funktionierende Formulierung mit deinem Team teilen."
      ],
      "fields": [
        [
          "Vorlage",
          "Der Prompt-Text mit seinen {{name}}-Variablen."
        ],
        [
          "Variablen",
          "Werden in der Vorlage automatisch erkannt."
        ],
        [
          "Zielmodell",
          "Allgemein, oder das Modell, für das der Prompt geschrieben wurde."
        ]
      ],
      "use": "Tab „Verwenden“: Lade das JSON herunter; das Python-Beispiel zeigt, wie du die Variablen ausfüllst."
    },
    "dataset": {
      "what": "Ein Dataset ist eine Sammlung von Beispielen im JSONL-Format (eine JSON-Zeile pro Beispiel), mit der ein Modell trainiert oder evaluiert wird.",
      "when": [
        "Ein Modell auf dein Fachgebiet feinabstimmen (mit einer LoRA-Konfiguration).",
        "Ein Modell an echten Fällen evaluieren."
      ],
      "fields": [
        [
          "Format",
          "Chat (Nachrichten), Instruktion oder Completion; wird automatisch erkannt."
        ],
        [
          "Inhalt",
          "Eingefügt oder importiert; große Dateien landen im Objektspeicher."
        ],
        [
          "Vorschau",
          "Die ersten Zeilen werden auf der Seite angezeigt."
        ]
      ],
      "use": "Tab „Verwenden“: Lade das JSONL herunter und öffne es mit der datasets-Bibliothek (Beispiel dabei) oder direkt in Axolotl."
    },
    "lora": {
      "what": "LoRA passt ein bestehendes Modell an eine Aufgabe an, ohne es komplett neu zu trainieren: Nur kleine Adapter werden trainiert. Eine LoRA-Seite bündelt alle Einstellungen dieses Trainings.",
      "when": [
        "Ein erfolgreiches Fine-Tuning reproduzieren.",
        "Dein eigenes Training mit bewährten Einstellungen starten."
      ],
      "fields": [
        [
          "Methode",
          "LoRA oder QLoRA (auf 4 Bit komprimiertes Modell, weniger Speicher)."
        ],
        [
          "Basismodell",
          "Das anzupassende Modell, z. B. Qwen/Qwen2.5-7B-Instruct."
        ],
        [
          "Rank, Alpha, Dropout",
          "Größe und Stärke der Adapter."
        ],
        [
          "Lernrate, Epochen, Batch",
          "Trainingseinstellungen."
        ],
        [
          "Verknüpftes Dataset",
          "Das Dataset aus dem Katalog, das fürs Training genutzt wurde."
        ]
      ],
      "use": "Tab „Verwenden“: Lade die YAML-Konfiguration für Axolotl herunter oder kopiere das PEFT-Beispiel in Python."
    },
    "tool": {
      "what": "Ein MCP-Server (Model Context Protocol) gibt einem KI-Assistenten neue Fähigkeiten: Dateien lesen, eine Datenbank abfragen, einen Dienst aufrufen. Derselbe Server funktioniert mit Claude, Cursor und anderen Assistenten.",
      "when": [
        "Einen Assistenten mit deinen Tools oder Daten verbinden.",
        "Einen selbst gebauten Server teilen."
      ],
      "fields": [
        [
          "Servername",
          "Kurze Kennung: Buchstaben, Ziffern, _ und -."
        ],
        [
          "Transport",
          "stdio (per Befehl auf deinem Rechner gestartet) oder HTTP (entfernter Server)."
        ],
        [
          "Befehl oder URL",
          "Wie der Server gestartet oder erreicht wird."
        ],
        [
          "Umgebungsvariablen",
          "Anzugebende Schlüssel (nur Namen, niemals Werte)."
        ]
      ],
      "use": "Tab „Verwenden“: Kopiere den Befehl claude mcp add für Claude Code oder den mcpServers-Block für Claude Desktop und Cursor."
    },
    "model": {
      "what": "Ein Modell ist ein KI-Modell, das von einem verifizierten Lab veröffentlicht wurde: Fine-Tune, Merge oder quantisierte Version. Die Seite beschreibt das Modell und verlinkt den Download.",
      "when": [
        "Ein Modell finden, das zu einer Aufgabe oder deiner Hardware passt.",
        "Das von deinem Lab trainierte Modell veröffentlichen (Lab-Status erforderlich)."
      ],
      "fields": [
        [
          "Typ",
          "Fine-Tune, Merge, quantisiert oder Basismodell."
        ],
        [
          "Basismodell, Familie, Größe",
          "Woher das Modell stammt und wie viele Parameter es hat."
        ],
        [
          "Format und Quantisierung",
          "safetensors, GGUF… und Kompressionsstufe."
        ],
        [
          "Training",
          "Verwendete Datasets und LoRA-Konfiguration, Epochen, Datum."
        ],
        [
          "Hardware",
          "Minimaler VRAM, CPU-Unterstützung, Geschwindigkeit."
        ],
        [
          "Nutzung und Evaluationen",
          "Sprachen, Einsatzzwecke, Grenzen, Benchmarks, Versionen."
        ]
      ],
      "use": "Button „Modell herunterladen“, dann Tab „Verwenden“ für Befehle zu llama.cpp, Ollama oder Transformers."
    },
    "agent": {
      "what": "Ein Agent ist ein KI-Assistent, der mehrere Schritte verkettet, um eine Aufgabe zu erledigen: Er folgt Anweisungen, nutzt MCP-Server und Kontexte und hält Leitplanken ein.",
      "when": [
        "Eine mehrstufige Aufgabe automatisieren (Support, Monitoring, Dokumentensortierung).",
        "Einen funktionierenden Agenten teilen, bereit zum erneuten Ausführen."
      ],
      "fields": [
        [
          "Anweisungen",
          "Rolle und Regeln des Agenten."
        ],
        [
          "Schritte",
          "Der erwartete Ablauf, ein Schritt pro Zeile."
        ],
        [
          "Framework",
          "Claude Agent SDK, LangGraph, CrewAI…"
        ],
        [
          "MCP-Server und Kontexte",
          "Ressourcen aus dem Katalog, die der Agent nutzt."
        ],
        [
          "Leitplanken",
          "Was der Agent niemals tun darf."
        ]
      ],
      "use": "Tab „Verwenden“: Lade das JSON des Agenten herunter; das Python-Beispiel führt ihn mit der Anthropic API aus."
    },
    "skill": {
      "what": "Ein Skill ist ein Anweisungspaket (Datei SKILL.md), das ein Assistent wie Claude nur lädt, wenn die Aufgabe es erfordert. Er vermittelt eine genaue Arbeitsweise.",
      "when": [
        "Dem Assistenten eine hauseigene Methode geben (Protokoll, Review, Bericht).",
        "Nicht mehr in jeder Unterhaltung dieselben Anweisungen wiederholen."
      ],
      "fields": [
        [
          "Name des Skills",
          "Kurze Kennung, Kleinbuchstaben und Bindestriche."
        ],
        [
          "Wann verwenden",
          "Der Satz, der dem Assistenten sagt, wann er den Skill laden soll."
        ],
        [
          "Anweisungen",
          "Der Inhalt von SKILL.md, in Markdown."
        ],
        [
          "Dateien und Ressourcen",
          "Zugehörige Skripte oder Vorlagen (optional)."
        ]
      ],
      "use": "Lade SKILL.md herunter und lege es in ~/.claude/skills/<name>/ ab (oder in .claude/skills/ in einem Projekt)."
    },
    "eval": {
      "what": "Eine Evaluation ist eine Reihe von Testfällen (Eingabe und erwartete Antwort) mit einer Bewertungsmethode. Sie misst, ob ein Modell, Prompt, Kontext oder Agent seine Aufgabe erfüllt.",
      "when": [
        "Zwei Prompts oder Modelle an denselben Fällen vergleichen.",
        "Prüfen, dass eine Änderung nichts kaputt gemacht hat."
      ],
      "fields": [
        [
          "Bewertete Ressource",
          "Die getestete Katalogseite (optional)."
        ],
        [
          "Bewertungsmethode",
          "Enthält, exakt, regulärer Ausdruck oder von einem Modell bewertet."
        ],
        [
          "Bestehensgrenze",
          "Der Anteil bestandener Fälle, der erreicht werden muss."
        ],
        [
          "Testfälle",
          "Eingaben und erwartete Antworten."
        ]
      ],
      "use": "Tab „Verwenden“: Lade das JSONL der Fälle herunter; das Python-Beispiel berechnet das Ergebnis."
    },
    "rag": {
      "what": "Eine RAG-Pipeline (Retrieval-Augmented Generation) lässt ein Modell anhand deiner Dokumente antworten: Sie werden in Chunks zerlegt und eingebettet, dann werden für jede Frage die passenden Auszüge gesucht und dem Modell übergeben.",
      "when": [
        "Einen Assistenten anhand interner Dokus oder eines Produktkatalogs antworten lassen.",
        "Halluzinationen verringern, indem das Modell seine Quellen nennt."
      ],
      "fields": [
        [
          "Quellen",
          "Verwendete Dokumente und wie sie aktualisiert werden."
        ],
        [
          "Chunking",
          "Chunk-Größe und Überlappung."
        ],
        [
          "Embeddings und Vektordatenbank",
          "Das Embedding-Modell und wo die Vektoren gespeichert werden."
        ],
        [
          "Retrieval",
          "Anzahl der behaltenen Auszüge und optionales Reranking."
        ],
        [
          "Prompt-Vorlage",
          "Der Text, der an das Modell geht, mit {{context}} und {{question}}."
        ]
      ],
      "use": "Tab „Verwenden“: Lade die JSON-Konfiguration herunter; das Python-Beispiel beschreibt jeden Schritt."
    },
    "harness": {
      "what": "Ein Harness ist die Umgebung, in der ein Agent läuft: seine Anweisungsdatei (z. B. CLAUDE.md), die erlaubten Tools, was verboten ist, Hooks und verbundene MCP-Server.",
      "when": [
        "Eine Team-Konfiguration für Claude Code oder einen anderen Assistenten teilen.",
        "Einen Agenten einschränken: erlaubte Befehle, geschützte Dateien."
      ],
      "fields": [
        [
          "Harness",
          "Claude Code, Claude Agent SDK, Cursor…"
        ],
        [
          "Anweisungen",
          "Die Anweisungsdatei, die der Agent liest."
        ],
        [
          "Erlaubt / verboten",
          "Berechtigungen, eine Regel pro Zeile."
        ],
        [
          "Hooks",
          "Automatisch ausgelöste Aktionen (JSON)."
        ],
        [
          "MCP-Server",
          "Server aus dem Katalog, die verbunden werden."
        ]
      ],
      "use": "Tab „Verwenden“: Kopiere CLAUDE.md und .claude/settings.json in dein Projekt."
    }
  },
  it: {
    "context": {
      "what": "Un contesto è un insieme di istruzioni ed esempi forniti al modello di IA prima della domanda dell'utente. Orienta la risposta senza riaddestrare nulla: è l'in-context learning.",
      "when": [
        "Ottenere risposte in un formato preciso (JSON, tabella, tono del brand).",
        "Insegnare un compito al modello con pochi esempi (few-shot).",
        "Dare al modello conoscenze aggiornate o specifiche dell'azienda."
      ],
      "fields": [
        [
          "Tipo",
          "Few-shot (esempi), istruzione di sistema, conoscenza o persona."
        ],
        [
          "Istruzione di sistema",
          "Il ruolo e le regole del modello."
        ],
        [
          "Esempi",
          "Coppie input / output atteso; spesso ne bastano da 2 a 10."
        ],
        [
          "Conoscenza",
          "Testo di riferimento che il modello deve usare."
        ],
        [
          "Modello target",
          "Generico, oppure una famiglia e un modello specifico per cui è stato ottimizzato."
        ]
      ],
      "use": "Scheda “Usa”: copia il JSON e inserisci i messaggi prima della domanda dell'utente. È fornito un esempio Python con l'API Anthropic."
    },
    "prompt": {
      "what": "Un prompt è un template di testo riutilizzabile con variabili tra doppie graffe, per esempio {{product}}. Compila le variabili, poi invialo al modello.",
      "when": [
        "Standardizzare una richiesta ricorrente (riassunto, traduzione, classificazione).",
        "Condividere con il tuo team una formulazione che funziona bene."
      ],
      "fields": [
        [
          "Template",
          "Il testo del prompt con le sue variabili {{name}}."
        ],
        [
          "Variabili",
          "Rilevate automaticamente nel template."
        ],
        [
          "Modello target",
          "Generico, oppure il modello per cui è stato scritto il prompt."
        ]
      ],
      "use": "Scheda “Usa”: scarica il JSON; l'esempio Python mostra come compilare le variabili."
    },
    "dataset": {
      "what": "Un dataset è un insieme di esempi in formato JSONL (una riga JSON per esempio) usato per addestrare o valutare un modello.",
      "when": [
        "Fare il fine-tuning di un modello sul tuo dominio (con una config LoRA).",
        "Valutare un modello su casi reali."
      ],
      "fields": [
        [
          "Formato",
          "Chat (messaggi), istruzione o completamento; rilevato automaticamente."
        ],
        [
          "Contenuto",
          "Incollato o importato; i file grandi vanno nello storage a oggetti."
        ],
        [
          "Anteprima",
          "Le prime righe sono mostrate nella pagina."
        ]
      ],
      "use": "Scheda “Usa”: scarica il JSONL e caricalo con la libreria datasets (esempio fornito) o direttamente in Axolotl."
    },
    "lora": {
      "what": "LoRA adatta un modello esistente a un compito senza riaddestrarlo del tutto: si addestrano solo piccoli adattatori. Una pagina LoRA raccoglie tutti i parametri di quell'addestramento.",
      "when": [
        "Riprodurre un fine-tuning che ha funzionato.",
        "Avviare il tuo addestramento partendo da parametri collaudati."
      ],
      "fields": [
        [
          "Metodo",
          "LoRA, o QLoRA (modello compresso a 4 bit, meno memoria)."
        ],
        [
          "Modello di base",
          "Il modello da adattare, es. Qwen/Qwen2.5-7B-Instruct."
        ],
        [
          "Rank, alpha, dropout",
          "Dimensione e intensità degli adattatori."
        ],
        [
          "Learning rate, epoche, batch",
          "Parametri di addestramento."
        ],
        [
          "Dataset collegato",
          "Il dataset del catalogo usato per l'addestramento."
        ]
      ],
      "use": "Scheda “Usa”: scarica la config YAML per Axolotl, o copia l'esempio Python PEFT."
    },
    "tool": {
      "what": "Un server MCP (Model Context Protocol) dà nuove capacità a un assistente di IA: leggere file, interrogare un database, chiamare un servizio. Lo stesso server funziona con Claude, Cursor e altri assistenti.",
      "when": [
        "Collegare un assistente ai tuoi strumenti o dati.",
        "Condividere un server che hai creato."
      ],
      "fields": [
        [
          "Nome del server",
          "Identificatore breve: lettere, cifre, _ e -."
        ],
        [
          "Trasporto",
          "stdio (avviato da un comando sul tuo computer) o HTTP (server remoto)."
        ],
        [
          "Comando o URL",
          "Come avviare o raggiungere il server."
        ],
        [
          "Variabili d'ambiente",
          "Chiavi da fornire (solo i nomi, mai i valori)."
        ]
      ],
      "use": "Scheda “Usa”: copia il comando claude mcp add per Claude Code, o il blocco mcpServers per Claude Desktop e Cursor."
    },
    "model": {
      "what": "Un modello è un modello di IA pubblicato da un Lab verificato: fine-tune, merge o versione quantizzata. La pagina descrive il modello e rimanda al download.",
      "when": [
        "Trovare un modello adatto a un compito o al tuo hardware.",
        "Pubblicare il modello addestrato dal tuo Lab (serve lo status di Lab)."
      ],
      "fields": [
        [
          "Tipo",
          "Fine-tune, merge, quantizzato o modello di base."
        ],
        [
          "Modello di base, famiglia, dimensione",
          "Da dove viene il modello e quanti parametri ha."
        ],
        [
          "Formato e quantizzazione",
          "safetensors, GGUF… e livello di compressione."
        ],
        [
          "Addestramento",
          "Dataset e config LoRA usati, epoche, data."
        ],
        [
          "Hardware",
          "VRAM minima, supporto CPU, velocità."
        ],
        [
          "Uso e valutazioni",
          "Lingue, casi d'uso, limiti, benchmark, versioni."
        ]
      ],
      "use": "Pulsante “Scarica il modello”, poi la scheda “Usa” per i comandi llama.cpp, Ollama o Transformers."
    },
    "agent": {
      "what": "Un agente è un assistente di IA che concatena più passaggi per completare un compito: segue istruzioni, usa server MCP e contesti e rispetta dei limiti di sicurezza.",
      "when": [
        "Automatizzare un compito in più passaggi (assistenza, monitoraggio, smistamento di documenti).",
        "Condividere un agente funzionante, pronto da rieseguire."
      ],
      "fields": [
        [
          "Istruzioni",
          "Il ruolo e le regole dell'agente."
        ],
        [
          "Passaggi",
          "Il flusso previsto, un passaggio per riga."
        ],
        [
          "Framework",
          "Claude Agent SDK, LangGraph, CrewAI…"
        ],
        [
          "Server MCP e contesti",
          "Risorse del catalogo usate dall'agente."
        ],
        [
          "Limiti di sicurezza",
          "Cosa l'agente non deve mai fare."
        ]
      ],
      "use": "Scheda “Usa”: scarica il JSON dell'agente; l'esempio Python lo esegue con l'API Anthropic."
    },
    "skill": {
      "what": "Una skill è un pacchetto di istruzioni (file SKILL.md) che un assistente come Claude carica solo quando il compito lo richiede. Insegna un modo preciso di fare le cose.",
      "when": [
        "Dare all'assistente un metodo interno (verbali, revisione, report).",
        "Smettere di ripetere le stesse istruzioni in ogni conversazione."
      ],
      "fields": [
        [
          "Nome della skill",
          "Identificatore breve, minuscole e trattini."
        ],
        [
          "Quando usarla",
          "La frase che dice all'assistente quando caricare la skill."
        ],
        [
          "Istruzioni",
          "Il contenuto di SKILL.md, in Markdown."
        ],
        [
          "File e risorse",
          "Script o modelli collegati (facoltativi)."
        ]
      ],
      "use": "Scarica SKILL.md e mettilo in ~/.claude/skills/<name>/ (o in .claude/skills/ in un progetto)."
    },
    "eval": {
      "what": "Una valutazione è un insieme di casi di test (input e risposta attesa) con un metodo di punteggio. Misura se un modello, un prompt, un contesto o un agente fa il suo lavoro.",
      "when": [
        "Confrontare due prompt o modelli sugli stessi casi.",
        "Verificare che una modifica non abbia rotto nulla."
      ],
      "fields": [
        [
          "Risorsa valutata",
          "La pagina del catalogo sotto test (facoltativa)."
        ],
        [
          "Metodo di punteggio",
          "Contiene, esatta, espressione regolare o valutata da un modello."
        ],
        [
          "Soglia di superamento",
          "La quota di casi superati da raggiungere."
        ],
        [
          "Casi di test",
          "Input e risposte attese."
        ]
      ],
      "use": "Scheda “Usa”: scarica il JSONL dei casi; l'esempio Python calcola il punteggio."
    },
    "rag": {
      "what": "Una pipeline RAG (retrieval-augmented generation) permette a un modello di rispondere a partire dai tuoi documenti: vengono divisi in chunk e trasformati in embeddings, poi per ogni domanda si recuperano gli estratti utili e si passano al modello.",
      "when": [
        "Far rispondere un assistente a partire da documenti interni o da un catalogo prodotti.",
        "Ridurre le allucinazioni facendo citare le fonti al modello."
      ],
      "fields": [
        [
          "Fonti",
          "Documenti usati e come vengono aggiornati."
        ],
        [
          "Chunking",
          "Dimensione dei chunk e sovrapposizione."
        ],
        [
          "Embeddings e vector store",
          "Il modello di embedding e dove sono memorizzati i vettori."
        ],
        [
          "Recupero",
          "Numero di estratti conservati ed eventuale reranking."
        ],
        [
          "Template del prompt",
          "Il testo inviato al modello, con {{context}} e {{question}}."
        ]
      ],
      "use": "Scheda “Usa”: scarica la config JSON; l'esempio Python descrive ogni passaggio."
    },
    "harness": {
      "what": "Un harness è l'ambiente che esegue un agente: il suo file di istruzioni (es. CLAUDE.md), gli strumenti che può usare, ciò che è vietato, gli hook e i server MCP collegati.",
      "when": [
        "Condividere una configurazione di team per Claude Code o un altro assistente.",
        "Vincolare un agente: comandi consentiti, file protetti."
      ],
      "fields": [
        [
          "Harness",
          "Claude Code, Claude Agent SDK, Cursor…"
        ],
        [
          "Istruzioni",
          "Il file di istruzioni che l'agente legge."
        ],
        [
          "Consentiti / negati",
          "Permessi, una regola per riga."
        ],
        [
          "Hook",
          "Azioni attivate automaticamente (JSON)."
        ],
        [
          "Server MCP",
          "Server del catalogo da collegare."
        ]
      ],
      "use": "Scheda “Usa”: copia CLAUDE.md e .claude/settings.json nel tuo progetto."
    }
  }
};
export const docOf = (lang, kind) => (DOCS[lang] || DOCS.fr)[kind] || DOCS.fr[kind];
