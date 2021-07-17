var indices = [];
for (var i = 0; i < data_source.get_length(); i++) {
    let anime_score = data_source.data["anime_scores"][i];
    let anime_view_count = data_source.data["anime_view_counts"][i];
    let anime_name_lower = data_source.data["name"][i].toLowerCase();

    if (
        anime_score >= score_slider.value[0] &&
        anime_score <= score_slider.value[1] &&
        anime_view_count >= view_counter_silider.value[0] &&
        anime_view_count <= view_counter_silider.value[1] &&
        !(only_new_toggle.active && !data_source.data["is_new"][i]) &&
        !(ignore_wip_toggle.active && anime_score == -1) &&
        !(ignore_wip_toggle.active && anime_view_count == -1) &&
        !(text_input.value.length > 0 && !anime_name_lower.includes(text_input.value.toLowerCase()))
    ) {
        indices.push(true);
    } else {
        indices.push(false);
    }
}
return indices;
