# API සඳහන

`sinling` යටතේ ලැයිස්තුගත සියල්ල ස්ථාවර පරිශීලක API වේ. ප්ලගින ලියන්නන් `sinling.registry` සහ
`sinling.resources` ද භාවිත කරයි. යටි ඉරකින් ආරම්භ වන modules පෞද්ගලික වේ. පහත විස්තර කේතයේ
docstrings වලින් ජනනය වන නිසා ඉංග්‍රීසියෙන් පවතී.

## කාර්ය {#tasks}

::: sinling.normalization.normalize

::: sinling.tokenization.tokenize

::: sinling.tokenization.sentences

::: sinling.stemming.stem

::: sinling.legacy_fonts.from_legacy_font

::: sinling.script.aksharas

## ලේඛන සහ නල මාර්ග {#documents-and-pipelines}

::: sinling.doc.Doc

::: sinling.doc.Token

::: sinling.doc.Span

::: sinling.pipeline.pipeline

::: sinling.pipeline.Pipeline

## ඇගයීම {#evaluation}

::: sinling.evaluation.evaluate

::: sinling.evaluation.Report

::: sinling.evaluation.datasets

::: sinling.evaluation.read_conllu

## Backends සහ ප්ලගින {#backends-and-plugins}

::: sinling.registry
    options:
      members: [Backend, BackendInfo, backends, register, get_backend, run_task, define_task, Task, ENTRY_POINT_GROUP]

## බාගැනීම් {#downloads}

::: sinling.resources
    options:
      members: [download, resource_path, Resource, register_resource, list_resources, cache_dir, is_offline]

## Backend පන්ති {#backend-classes}

::: sinling.normalization.RuleNormalizer

::: sinling.tokenization.RuleTokenizer

::: sinling.tokenization.RuleSentenceSplitter

::: sinling.stemming.SuffixStemmer

::: sinling.stemming.DictionaryStemmer

::: sinling.legacy_fonts.FMConverter

::: sinling.legacy_fonts.is_fm_font

## අක්ෂර වගු {#script-tables}

::: sinling.script
    options:
      members: [is_sinhala, CONSONANTS, INDEPENDENT_VOWELS, VOWEL_SIGNS, VOWEL_TO_SIGN]

## දෝෂ {#errors}

::: sinling.errors
