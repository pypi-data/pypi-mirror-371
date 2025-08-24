import pickle
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from transformers import BatchEncoding
from transformers.data import DataCollatorForLanguageModeling

import smirk
from test_tokenize_smiles import smile_strings  # noqa


def check_save(tokenizer):
    """Check that the tokenzier can be saved"""
    with TemporaryDirectory() as save_directory:
        files = tokenizer.save_pretrained(save_directory)
        assert len(files) == 3
        for file in files:
            file = Path(file)
            assert file.is_file()
            assert file.suffix == ".json"

        loaded = tokenizer.from_pretrained(save_directory)
    print("loaded: " + loaded.to_str())
    print("trained: " + tokenizer.to_str())
    assert isinstance(loaded, tokenizer.__class__)

    # Check pickling
    state = pickle.dumps(tokenizer)
    assert state is not None
    pickled = pickle.loads(state)
    assert pickled.to_str() == loaded.to_str()
    assert pickled.to_str() == tokenizer.to_str()
    smile = "[Fe+2].[Li+].[O-]P([O-])([O-])=O"
    assert pickled(smile) == tokenizer(smile)


def test_saving():
    tokenizer = smirk.SmirkTokenizerFast()
    check_save(tokenizer)


def test_vocab_size():
    tokenizer = smirk.SmirkTokenizerFast()
    assert len(tokenizer.get_vocab()) > 0
    assert len(tokenizer.get_vocab()) == len(tokenizer)


def check_tokenize(tokenizer):
    assert tokenizer.tokenize("Br") == ["Br"]
    assert tokenizer.tokenize("Sn[Sn]") == ["S", "n", "[", "Sn", "]"]


def check_normalizer(tokenizer):
    assert tokenizer.tokenize(" COO ") == ["C", "O", "O"]
    assert tokenizer.tokenize("[Ca++]") == ["Ca", "+", "2"]
    assert tokenizer.tokenize("[C--]") == ["C", "-", "2"]


def check_unknown(tokenizer):
    def check_tok(tokenizer, smi: str, unk: str = "🤷"):
        code = tokenizer(smi)["input_ids"]
        assert tokenizer.unk_token_id in code
        expected = smi.replace(unk, tokenizer.unk_token)
        assert smi != expected  # Sanity check the test
        assert "".join(tokenizer.tokenize(smi)) == expected

    check_tok(tokenizer, "🤷")
    check_tok(tokenizer, "C🤷")
    check_tok(tokenizer, "🤷C")
    check_tok(tokenizer, "[🤷]")
    check_tok(tokenizer, "[C🤷]")
    check_tok(tokenizer, "[🤷C]")


def test_tokenize():
    tokenizer = smirk.SmirkTokenizerFast()
    check_tokenize(tokenizer)


def test_unknown():
    tokenizer = smirk.SmirkTokenizerFast()
    check_unknown(tokenizer)


def test_special_tokens():
    tokenizer = smirk.SmirkTokenizerFast()
    vocab = tokenizer.get_vocab()
    assert tokenizer.unk_token_id == vocab["[UNK]"]
    assert tokenizer.mask_token_id == vocab["[MASK]"]
    assert tokenizer.pad_token_id == vocab["[PAD]"]
    assert tokenizer.bos_token_id == vocab["[BOS]"]
    assert tokenizer.eos_token_id == vocab["[EOS]"]


def test_pad(smile_strings):  # noqa F811
    tokenizer = smirk.SmirkTokenizerFast()
    code = tokenizer(smile_strings)
    assert len(code["input_ids"][0]) != len(code["input_ids"][1])
    code = tokenizer.pad(code)
    assert len(code["input_ids"][0]) == len(code["input_ids"][1])
    assert len(code["special_tokens_mask"][0]) == len(code["special_tokens_mask"][1])


@pytest.mark.parametrize("return_offsets_mapping", [True, False, None])
def test_encode(return_offsets_mapping):
    tokenizer = smirk.SmirkTokenizerFast()
    kwargs = {"return_offsets_mapping": return_offsets_mapping}
    code = tokenizer("NCCc1cc(O)c(O)cc1", **kwargs)
    assert "input_ids" in code
    assert "special_tokens_mask" in code
    assert "attention_mask" in code
    assert (
        tokenizer.decode(code["input_ids"], skip_special_tokens=True)
        == "NCCc1cc(O)c(O)cc1"
    )
    if return_offsets_mapping:
        assert "offset_mapping" in code


@pytest.mark.parametrize("return_offsets_mapping", [True, False, None])
def test_encode_batch(smile_strings, return_offsets_mapping):  # noqa F811
    tokenizer = smirk.SmirkTokenizerFast()
    kwargs = {"return_offsets_mapping": return_offsets_mapping}
    batch = tokenizer(smile_strings, **kwargs)
    assert "input_ids" in batch
    assert "special_tokens_mask" in batch
    assert "attention_mask" in batch
    assert (
        tokenizer.batch_decode_plus(batch["input_ids"], skip_special_tokens=True)
        == smile_strings
    )
    if return_offsets_mapping:
        assert "offset_mapping" in batch


def test_collate(smile_strings):  # noqa F811
    tokenizer = smirk.SmirkTokenizerFast()
    collate = DataCollatorForLanguageModeling(
        tokenizer, mlm_probability=0.5, return_tensors="np"
    )
    code = tokenizer(smile_strings)
    assert len(code["input_ids"]) == len(smile_strings)
    assert isinstance(code, BatchEncoding)
    assert "special_tokens_mask" in code.keys()

    # Collate batch
    collated_batch = collate(code)
    print(collated_batch)

    # Should pad to longest
    max_length = len(code["input_ids"][1])
    for k in [
        "input_ids",
        "token_type_ids",
        "attention_mask",
        "labels",
    ]:
        assert k in collated_batch.keys()
        assert collated_batch[k].shape == (2, max_length)

    # Check for padding
    n = len(code["input_ids"][0]) - 1
    collated_batch["input_ids"][0, n:] == tokenizer.pad_token_id

    # Check decode
    decode = tokenizer.batch_decode(collated_batch["input_ids"])
    assert tokenizer.pad_token in decode[0]
    assert tokenizer.mask_token in decode[0]
    assert tokenizer.mask_token in decode[1]
    decode_no_special = tokenizer.batch_decode(
        collated_batch["input_ids"], skip_special_tokens=True
    )
    assert len(decode_no_special[0]) < len(decode[0])
    assert tokenizer.pad_token not in decode_no_special[0]
