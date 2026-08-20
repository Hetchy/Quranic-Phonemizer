"""Which fixture exercises which rule of the catalogue.

The entries are the functions themselves, so a renamed one fails this
module's import rather than leaving a rule quietly uncovered.
"""
from __future__ import annotations

from collections.abc import Callable

from tests.adjacent.test_lam_qamariyyah import (
    test_the_article_lam_is_said_before_each_moon_letter as qamariyyah_each,
)
from tests.adjacent.test_lam_shamsiyyah import (
    test_the_article_lam_merges_into_each_sun_letter as shamsiyyah_each,
    test_the_rasm_writes_one_lam_where_the_article_meets_a_lam
    as shamsiyyah_lam,
)
from tests.adjacent.test_mutajanisayn_kamil import (
    test_a_daal_merges_wholly_into_a_taa_inside_one_word as kamil_inside,
    test_a_letter_merges_wholly_into_its_neighbour_of_the_same_family
    as kamil_across,
)
from tests.adjacent.test_mutajanisayn_naqis import (
    test_a_taa_takes_the_place_of_the_tah_but_not_its_heaviness as naqis_trace,
)
from tests.adjacent.test_mutamathilayn import (
    test_a_letter_merges_into_the_same_letter_across_a_boundary
    as mutamathilayn_across,
    test_the_same_merger_inside_one_word as mutamathilayn_inside,
)
from tests.adjacent.test_mutaqaribayn import (
    test_a_quiescent_lam_merges_into_a_following_raa as mutaqaribayn_lam,
    test_a_quiescent_qaaf_merges_into_a_kaaf_inside_one_word
    as mutaqaribayn_qaaf,
)
from tests.boundary.test_hamza_wasl_silent import (
    test_a_verb_hamza_drops_when_the_word_before_it_joins as wasl_silent_verb,
    test_the_article_hamza_drops_when_the_word_before_it_joins
    as wasl_silent_article,
)
from tests.boundary.test_hamza_wasl_start import (
    test_a_verb_whose_third_letter_carries_a_damma_takes_a_damma
    as wasl_damma,
    test_a_verb_whose_third_letter_carries_no_damma_takes_a_kasra
    as wasl_kasra,
    test_the_article_gives_the_prosthetic_hamza_a_fatha as wasl_fatha,
    test_the_seven_nouns_that_take_a_kasra_of_their_own as wasl_kasra_nouns,
)
from tests.boundary.test_ibdal_hamza import (
    test_a_quiescent_hamza_becomes_a_length_when_started_on as ibdal_started,
    test_the_ibdal_names_the_hamza_it_replaced as ibdal_subject,
    test_the_length_the_ibdal_made_takes_no_madd_beside_it as ibdal_alone,
)
from tests.boundary.test_iltiqa_insertions import (
    test_a_spelled_out_opening_takes_a_fatha_to_reach_the_divine_name
    as iltiqa_fatha_site,
    test_a_tanween_noon_takes_a_kasra_to_reach_the_next_word
    as iltiqa_kasra_site,
    test_that_fatha_is_put_in_rather_than_merged as iltiqa_fatha_insert,
    test_that_kasra_is_put_in_rather_than_merged as iltiqa_kasra_insert,
)
from tests.boundary.test_iltiqa_shortening import (
    test_a_long_vowel_shortens_before_a_quiescent_letter as shortening_madd,
    test_a_plural_waw_shortens_onto_a_word_whose_hamza_has_elided
    as shortening_waw,
)
from tests.laws.test_ishmam import (
    test_the_ishmam_classifies_the_consonant_and_owns_no_sound as ishmam_edge,
    test_the_ishmam_names_one_letter_and_reads_nothing_beside_it
    as ishmam_subject,
)
from tests.laws.test_madd_tabii import (
    test_an_ordinary_mid_word_long_vowel_takes_madd_tabii as tabii_ordinary,
    test_madd_tabii_names_the_vowel_it_lengthens_and_nothing_else
    as tabii_subject,
)
from tests.nasal.test_ghunnah_mushaddadah import (
    test_a_doubled_meem_is_held_through_the_nose as ghunnah_meem,
    test_a_noon_the_article_doubles_is_held_the_same_way as ghunnah_noon,
)
from tests.nasal.test_idgham_bi_ghunnah import (
    test_a_quiescent_noon_merges_with_a_hum_into_each_letter as bi_ghunnah_noon,
    test_a_tanween_merges_with_a_hum_into_each_letter as bi_ghunnah_tanween,
)
from tests.nasal.test_idgham_bila_ghunnah import (
    test_a_quiescent_noon_merges_into_a_lam_without_a_hum as bila_ghunnah_lam,
    test_a_quiescent_noon_merges_into_a_raa_without_a_hum as bila_ghunnah_raa,
)
from tests.nasal.test_idgham_shafawi import (
    test_a_quiescent_meem_merges_into_the_meem_of_the_next_word
    as idgham_shafawi_meem,
)
from tests.nasal.test_ikhfaa import (
    test_every_hiding_letter_hides_a_tanween_noon as ikhfaa_tanween,
    test_every_hiding_letter_hides_a_written_noon as ikhfaa_written,
)
from tests.nasal.test_ikhfaa_shafawi import (
    test_a_quiescent_meem_before_a_baa_is_hidden_at_the_lips
    as ikhfaa_shafawi_baa,
)
from tests.nasal.test_iqlab import (
    test_a_tanween_turns_when_a_baa_starts_the_next_word as iqlab_tanween,
    test_a_written_noon_before_a_baa_turns_inside_one_word as iqlab_written,
)
from tests.nasal.test_izhar import (
    test_every_throat_letter_keeps_a_tanween_noon_clear as izhar_tanween,
    test_every_throat_letter_keeps_a_written_noon_clear as izhar_written,
)
from tests.nasal.test_izhar_mutlaq import (
    test_the_four_words_hold_their_noon_against_a_glide as izhar_mutlaq,
)
from tests.nasal.test_izhar_shafawi import (
    test_a_quiescent_meem_before_a_daal_stays_clear as izhar_shafawi_daal,
    test_a_quiescent_meem_before_a_taa_stays_clear as izhar_shafawi_taa,
)
from tests.tafkheem.test_istilaa import (
    test_every_istilaa_letter_is_heavy as tafkheem_istilaa,
)
from tests.tafkheem.test_lam import (
    test_the_divine_name_is_heavy_in_every_shape_a_kasra_misses
    as tafkheem_lam,
)
from tests.tafkheem.test_raa import (
    test_a_raa_with_a_fatha_is_heavy as tafkheem_raa,
    test_a_raa_with_a_kasra_is_light as tarqeeq_raa,
)
from tests.test_madd import (
    test_a_long_vowel_before_a_hamza_in_the_same_word as muttasil_inside,
    test_a_long_vowel_before_a_letter_the_stop_silences as arid_stopped,
    test_a_long_vowel_before_a_quiescent_letter as lazim_sakin,
    test_a_long_vowel_before_a_doubled_letter_is_lazim as lazim_doubled,
    test_a_long_vowel_ending_a_word_before_a_hamza_opening_the_next
    as munfasil_across,
    test_a_quiescent_waw_after_a_fatha_before_the_stopped_letter as leen_waw,
)
from tests.test_one_offs import (
    test_the_one_imala_in_the_corpus as imala_site,
    test_the_one_ishmam_in_the_corpus as ishmam_site,
    test_the_one_tashil_in_the_corpus as tashil_site,
)
from tests.test_qalqala import (
    test_a_doubled_qalqala_letter_echoes_at_a_stop as qalqala_akbar,
    test_every_qalqala_letter_echoes_quiescent_inside_a_word as qalqala_sughra,
    test_every_qalqala_letter_echoes_when_the_stop_silences_it as qalqala_kubra,
)
from tests.waqf.test_final_glides import (
    test_that_waw_becomes_pure_length_at_a_stop as drop_before_a_glide,
)
from tests.waqf.test_madd_badal import (
    test_a_badal_before_a_permanent_sakin_keeps_the_madd_that_holds_it
    as badal_contextual,
    test_a_long_vowel_on_a_hamza_is_a_badal_and_not_a_plain_madd
    as badal_ordinary,
    test_the_plainest_badal_names_the_length_with_no_madd_beside_it
    as badal_plain,
)
from tests.waqf.test_madd_iwad import (
    test_a_fathatan_lengthens_the_letter_before_it_at_a_stop as iwad_length,
    test_the_iwad_names_the_letter_it_lengthened as iwad_subject,
)
from tests.waqf.test_seven_alifs import (
    test_each_pausal_alif_falls_silent_when_the_reading_carries_on
    as pausal_alif_joined,
    test_each_pausal_alif_is_sounded_when_it_is_stopped_on
    as pausal_alif_stopped,
)
from tests.waqf.test_silah import (
    test_a_haa_before_a_word_opening_hamza_is_held_the_longer_count
    as silah_before_a_hamza,
    test_the_pronoun_haa_is_long_when_the_reading_carries_on as silah_joined,
    test_the_same_haa_loses_its_length_at_a_stop as silah_drop,
    test_the_stop_leaves_no_second_drop_on_the_haa as silah_drop_alone,
)
from tests.waqf.test_waqf_diacritic_drop import (
    test_a_final_damma_is_dropped_at_a_stop as drop_damma,
    test_a_final_fatha_is_dropped_at_a_stop as drop_fatha,
    test_a_final_kasra_is_dropped_at_a_stop as drop_kasra,
)
from tests.waqf.test_waqf_taa_marbuta import (
    test_a_taa_marbuta_after_a_fathatan_becomes_a_haa_at_a_stop
    as taa_marbuta_tanween,
    test_a_taa_marbuta_is_read_as_a_haa_at_a_stop as taa_marbuta_haa,
)

Fixture = Callable[..., None]

#: Every rule id `tajweed_rules` publishes, and the cases that read it back
#: out by name. There is no room here for a rule with no case.
RULE_FIXTURES: dict[str, tuple[Fixture, ...]] = {
    "izhar": (izhar_written, izhar_tanween, izhar_mutlaq),
    "ikhfaa": (ikhfaa_written, ikhfaa_tanween),
    "iqlab": (iqlab_written, iqlab_tanween),
    "idgham_bi_ghunnah": (bi_ghunnah_noon, bi_ghunnah_tanween),
    "idgham_bila_ghunnah": (bila_ghunnah_raa, bila_ghunnah_lam),
    "ghunnah_mushaddadah": (ghunnah_meem, ghunnah_noon),
    "izhar_shafawi": (izhar_shafawi_daal, izhar_shafawi_taa),
    "ikhfaa_shafawi": (ikhfaa_shafawi_baa,),
    "idgham_shafawi": (idgham_shafawi_meem,),
    "idgham_mutamathilayn": (mutamathilayn_across, mutamathilayn_inside),
    "idgham_mutaqaribayn": (mutaqaribayn_lam, mutaqaribayn_qaaf),
    "idgham_mutajanisayn_kamil": (kamil_across, kamil_inside),
    "idgham_mutajanisayn_naqis": (naqis_trace,),
    "lam_shamsiyyah": (shamsiyyah_each, shamsiyyah_lam),
    "lam_qamariyyah": (qamariyyah_each,),
    "qalqala_sughra": (qalqala_sughra,),
    "qalqala_kubra": (qalqala_kubra,),
    "qalqala_akbar": (qalqala_akbar,),
    "tafkheem": (tafkheem_istilaa, tafkheem_raa, tafkheem_lam),
    "tarqeeq": (tarqeeq_raa,),
    "imala": (imala_site,),
    "tashil": (tashil_site,),
    "ishmam": (ishmam_site, ishmam_subject, ishmam_edge),
    "madd_tabii": (tabii_ordinary, tabii_subject),
    "madd_wajib_muttasil": (muttasil_inside,),
    "madd_jaiz_munfasil": (munfasil_across, silah_before_a_hamza),
    "madd_lazim": (lazim_sakin, lazim_doubled),
    "madd_arid_lissukun": (arid_stopped,),
    "madd_leen": (leen_waw,),
    "madd_iwad": (iwad_length, iwad_subject),
    "madd_badal": (badal_ordinary, badal_plain, badal_contextual),
    "madd_silah": (silah_joined, silah_before_a_hamza),
    "ibdal_hamza": (ibdal_started, ibdal_subject, ibdal_alone),
    "hamza_wasl_silent": (wasl_silent_article, wasl_silent_verb),
    "hamza_wasl_fatha": (wasl_fatha,),
    "hamza_wasl_kasra": (wasl_kasra, wasl_kasra_nouns),
    "hamza_wasl_damma": (wasl_damma,),
    "iltiqa_kasra": (iltiqa_kasra_site, iltiqa_kasra_insert),
    "iltiqa_fatha": (iltiqa_fatha_site, iltiqa_fatha_insert),
    "iltiqa_shortening": (shortening_madd, shortening_waw),
    "waqf_diacritic_drop": (
        drop_fatha, drop_damma, drop_kasra, drop_before_a_glide,
    ),
    "waqf_silah_drop": (silah_drop, silah_drop_alone),
    "waqf_taa_marbuta": (taa_marbuta_haa, taa_marbuta_tanween),
    "pausal_alif": (pausal_alif_stopped, pausal_alif_joined),
}
