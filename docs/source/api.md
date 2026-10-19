# API reference

Everything listed under `sinling` is the stable user API. Plugin authors also use
`sinling.registry` and `sinling.resources`. Modules whose names start with an underscore are
private.

## Tasks

::: sinling.normalization.normalize

::: sinling.tokenization.tokenize

::: sinling.tokenization.sentences

::: sinling.stemming.stem

::: sinling.legacy_fonts.from_legacy_font

::: sinling.script.aksharas

## Documents and pipelines

::: sinling.doc.Doc

::: sinling.doc.Token

::: sinling.doc.Span

::: sinling.pipeline.pipeline

::: sinling.pipeline.Pipeline

## Evaluation

::: sinling.evaluation.evaluate

::: sinling.evaluation.Report

::: sinling.evaluation.datasets

::: sinling.evaluation.read_conllu

## Backends and plugins

::: sinling.registry
    options:
      members: [Backend, BackendInfo, backends, register, get_backend, run_task, define_task, Task, ENTRY_POINT_GROUP]

## Downloads

::: sinling.resources
    options:
      members: [download, resource_path, Resource, register_resource, list_resources, cache_dir, is_offline]

## Backend classes

::: sinling.normalization.RuleNormalizer

::: sinling.tokenization.RuleTokenizer

::: sinling.tokenization.RuleSentenceSplitter

::: sinling.stemming.SuffixStemmer

::: sinling.stemming.DictionaryStemmer

::: sinling.legacy_fonts.FMConverter

::: sinling.legacy_fonts.is_fm_font

## Script tables

::: sinling.script
    options:
      members: [is_sinhala, CONSONANTS, INDEPENDENT_VOWELS, VOWEL_SIGNS, VOWEL_TO_SIGN]

## Errors

::: sinling.errors
