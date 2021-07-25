var selected_animes = [];
for (var i = 0; i < data_source.get_length(); i++) {
    let score = data_source.data["score"][i];
    let view_count = data_source.data["view_count"][i];
    let anime_name_lower = data_source.data["name"][i].toLowerCase();

    if (
        score >= score_slider.value[0] &&
        score <= score_slider.value[1] &&
        view_count >= view_counter_silider.value[0] &&
        view_count <= view_counter_silider.value[1] &&
        !(only_new_toggle.active && !data_source.data["is_new"][i]) &&
        !(ignore_wip_toggle.active && score == -1) &&
        !(ignore_wip_toggle.active && view_count == -1) &&
        !(text_input.value.length > 0 && !anime_name_lower.includes(text_input.value.toLowerCase()))
    ) {
        selected_animes.push(data_source.data["name"][i]);
    }
}


if (selected_animes.length > 0) {
    ani_select.options = selected_animes;
} else {
    ani_select.options = ["無符合條件之作品"];
}

ani_select.value = ani_select.options[0];
