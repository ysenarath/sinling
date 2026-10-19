# API සඳහන

Sinling හි සෑම ශ්‍රිතයක්ම සහ class එකක්ම, ඒවායේ විකල්ප සමඟ. බොහෝ දෙනෙකුට අවශ්‍ය වන්නේ "කාර්ය"
සහ "ලේඛන සහ නල මාර්ග" යටතේ ඇති ශ්‍රිත පමණි. ඉන් පසු ඇති කොටස් ප්ලගින ලියන අය සඳහාය. මෙම පිටුව
කේතයෙන් ස්වයංක්‍රීයව සෑදෙන නිසා, විස්තර ඉංග්‍රීසියෙන් පමණක් ඇත.

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
