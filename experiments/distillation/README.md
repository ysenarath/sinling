# Distilling English-to-Sinhala translation into one small model

The [translation experiment](../translation/) found that cheap LLMs translate English into Sinhala
reasonably well, but they are slow and cost money for every sentence. This experiment tests
whether a small model that runs anywhere can learn to translate as well, by training it on
translations made by several larger models (the "teachers").

The plan:

1. **Pilot:** compare open teacher models on FLORES-200 `dev`, and measure how fast each one
   translates.
2. Have the best teachers translate a large, openly licensed English corpus.
3. For each sentence, keep the translation the teachers agree on most, and drop poor ones.
4. Train a small student model on the result.
5. Score the student on FLORES-200 `devtest`, against the teachers and the models from the
   translation experiment.

## Teachers

Only models whose licence lets us train on their output and ship the result under Apache-2.0:

| Model | Licence | Size |
| --- | --- | --- |
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | Apache-2.0 | 27.8B |
| [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) | Apache-2.0 | 117B (5.1B active) |
| [GLM-4.7-Flash](https://huggingface.co/zai-org/GLM-4.7-Flash) | MIT | 31B |
| [Ministral-3-14B-Instruct](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512) | Apache-2.0 | 14B |

Llama, Gemma 3 (and TranslateGemma, which is built on it) and NLLB are left out: a model trained
on their output would carry their licence terms, and NLLB doesn't allow commercial use. Gemma 4
(2026) is Apache-2.0, so it can be a teacher or the student; it hasn't been benchmarked yet.

## Running the pilot on Hopper

The pilot runs on George Mason University's Hopper cluster, on one A100 80GB GPU, and should
take about an hour. Each model is started with [vLLM](https://docs.vllm.ai/), translates
the 997 `dev` sentences with the plain prompt from the translation experiment, and is stopped.

Copy the code, the FLORES text files and the Sinling wheel to `/scratch/$USER/sinling-exp` on
Hopper, keeping the `translation/` and `distillation/` folder names. Then, from that folder on the
login node:

```
bash distillation/hopper/setup.sh        # once: Python environment and models (about 215 GB)
sbatch distillation/hopper/pilot.sbatch
```

The translations land in `distillation/data/teachers/`. Score them with the translation
experiment's script:

```
../translation/run.sh score.py "$PWD"/data/teachers/*/base_dev.jsonl
```

Each `.speed.json` file next to the translations records how many sentences an hour the model
translates on one GPU.

## Pilot results

Run on 2026-10-19 and 2026-10-20: the 997 FLORES-200 `dev` sentences, the plain prompt, chrF++
after `sinling.normalize()`. The open LLMs used greedy decoding. The closed models, run through
OpenRouter, don't accept a temperature setting, so they ran with their default; they are included as
references only, since OpenAI's and Anthropic's terms don't allow training competing models on
their output. Claude Sonnet 5.5 can't run with its thinking switched off, so it used the lowest
thinking effort. The dedicated translation models (NLLB, MADLAD, Aya, M2M) used beam search with 4
beams instead of greedy decoding, the usual setting for them.

| Model | chrF++ | vs GPT-6 Luna (95% interval) | Cost, or sentences an hour on one A100 |
| --- | --- | --- | --- |
| GPT-6 Luna | 48.3 | — | $0.05 |
| Claude Sonnet 5.5 | 46.5 | −1.8 (−2.3 to −1.2) | $1.82 |
| Claude Haiku 5.5 | 43.7 | −4.6 (−5.2 to −3.9) | $0.08 |
| NLLB-200 3.3B (non-commercial licence) | 43.2 | −5.1 (−6.0 to −4.3) | 40,000 |
| MADLAD-400 10.7B | 40.6 | −7.7 (−8.5 to −6.9) | 10,500 |
| Qwen3.8-27B | 38.9 | −9.4 (−10.1 to −8.8) | 27,700 |
| Aya-101 | 37.8 | −10.5 (−11.7 to −9.4) | 11,000 |
| gpt-oss-120b | 35.6 | −12.7 (−13.9 to −11.5) | 54,500 |
| M2M-100 1.2B | 31.4 | −16.9 (−17.7 to −16.1) | 35,000 |
| GLM-4.7-Flash | 29.6 | −18.7 (−19.8 to −17.6) | 15,600 |
| Ministral-3-14B-Instruct | 6.4 | — | 6,000 |
| MADLAD-400 3B | 0.0 | — | 4,600 |

- **GPT-6 Luna is the best and the cheapest closed model here.** Claude Sonnet 5.5 comes close at 36
  times the cost; Claude Haiku 5.5 is 4.6 points behind Luna at a similar price.
- **Dedicated translation models beat the general open LLMs.** NLLB-200 3.3B is the best open model,
  4.3 points (3.4 to 5.2) ahead of Qwen3.8-27B, but its licence doesn't allow commercial use, so it
  can only be a benchmark. MADLAD-400 10.7B is the best model we could train a student on: 1.7
  points (0.9 to 2.6) ahead of Qwen3.8-27B, and still 7.7 behind Luna.
- **NLLB, Aya and M2M can't write the zero-width joiner.** Their output has a space where ්‍ය and
  ්‍ර should be (විද් යාලයේ for විද්‍යාලයේ), which splits words. Putting the joiner back after
  every hal mark followed by a space and ය or ර raises NLLB to about 45.4. That repair is only an
  estimate: the same pattern also occurs between real words (203 times in the references).
- **NLLB sometimes drops most of a sentence** (64 outputs under half the reference length) or
  invents text, such as "[23වන පිටුවේ පින්තූරය]" ("[picture on page 23]").
- **MADLAD-400 3B produced no Sinhala**: only repeated Thai, Chinese or Latin fragments. The
  10.7B model worked with the same prompt and settings, so this is likely a problem with the 3B
  weights in bfloat16; untested in float32.
- **Ministral can't write Sinhala:** most of its output repeats one made-up word until it runs out of
  tokens. GLM (54 sentences) and gpt-oss (9) sometimes get stuck the same way, which a filter
  step would catch.
- **Speed isn't a problem.** 200,000 sentences would take about 7 GPU-hours with Qwen3.8-27B.

## Finding the best model at low cost

Run on 2026-10-20 through OpenRouter, in three rounds, each on fewer models and more sentences:

1. **3 sentences** from each of 15 new models, to catch errors. Mistral Large 4 wrote Thai and English,
   and Hunyuan-MT2 30B wrote Kannada, so both were dropped. Muse Spark 1.3 was left out on price,
   and Qwen3.8 Flash was rate-limited.
2. **The first 100 `dev` sentences** from the remaining 12 models.
3. **The leaders on more sentences:** DeepSeek v4.1 Flash on all 997, and Gemini 4 Argon and
   Gemini 3.8 Flash on the first 400.

The three rounds cost $1.02 in total.

| Model | chrF++, first 400 | vs GPT-6 Luna (95% interval) | USD per 1,000 sentences |
| --- | --- | --- | --- |
| Gemini 4 Argon | 51.0 | +1.8 (+1.0 to +2.5) | 1.25 |
| Gemini 3.8 Flash | 49.5 | +0.3 (−0.5 to +1.0) | 0.33 |
| DeepSeek v4.1 Flash | 49.3 | +0.1 (−0.8 to +1.0) | 0.06 |
| GPT-6 Luna | 49.2 | — | 0.05 |
| Claude Sonnet 5.5 | 46.9 | −2.3 (−3.3 to −1.5) | 1.82 |

On the first 100 sentences, these models were level with GPT-6 Luna: GPT-6 Luna Pro,
DeepSeek v4 Pro and DeepSeek v4.1 Flash (1017). GPT-6.1 Sol was 0.7 points behind it.
These were clearly behind:

| Model | chrF++, first 100 |
| --- | --- |
| Gemini 2.5 Flash-Lite | −2.3 |
| GLM-5.3 | −3.9 |
| MiMo v2.6 Flash | −5.1 |
| Command A+ | −16.6 |

- **Gemini 4 Argon is the best translator**, the only model clearly ahead of Luna, but it costs 26
  times as much.
- **DeepSeek v4.1 Flash is the best value.** On all 997 sentences it beats Luna by 0.7 (+0.1 to
  +1.2), at about the same price, and it led the translation experiment on `devtest` too. Its
  weights are MIT-licensed. If its API terms allow it, it is the strongest teacher we can use for
  distillation.
- Gemini 3.8 Flash and Gemini 4 Argon sometimes add the English name in brackets after a
  transliterated one: පීබීඑස් (PBS). This costs them a little chrF++.
