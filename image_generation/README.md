# Image Generation — Cute Dog

Generates a colorful 3D cartoon dog image via **OpenAI DALL-E 3**.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key (choose one):

   **Option A — environment variable:**
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY = "sk-..."
   ```

   **Option B — `.env` file** (create `image_generation/.env`):
   ```
   OPENAI_API_KEY=sk-...
   ```

## Run

```bash
python generate_dog.py
```

The image is saved in the `outputs/` folder as `cute_dog_YYYYMMDD_HHMMSS.png`.

## Prompt

> A cute dog in a colorful 3D cartoon style, slightly turned away from the camera,
> with a clear heart-shaped marking on its butt fur, playful and funny expression,
> bright colors, simple background, soft lighting, high detail.
