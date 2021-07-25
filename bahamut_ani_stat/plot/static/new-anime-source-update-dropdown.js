console.log(cb_obj.value);

if (cb_obj.value != "無符合條件之作品") {
    view_source.data["insert_times"] = view_counts_source_dict[cb_obj.value].data["insert_times"];
    view_source.data["view_counts"] = view_counts_source_dict[cb_obj.value].data["view_counts"];

    score_source.data["scores"] = score_source_dict[cb_obj.value].data["scores"];
    score_source.data["insert_times"] = score_source_dict[cb_obj.value].data["insert_times"];
} else {
    view_source.data["insert_times"] = [];
    view_source.data["view_counts"] = [];

    score_source.data["scores"] = [];
    score_source.data["insert_times"] = [];
}

view_source.change.emit();
score_source.change.emit();
