const name = cb_obj.value;

if (name === "無符合條件之作品") {
    view_source.data = { insert_times: [], view_counts: [] };
    score_source.data = { insert_times: [], scores: [] };
    view_source.change.emit();
    score_source.change.emit();
} else {
    const sn = name_to_sn[name];
    fetch(data_path + "/" + sn + ".json")
        .then(r => r.json())
        .then(d => {
            view_source.data = {
                insert_times: d.view_counts.insert_times,
                view_counts: d.view_counts.view_counts,
            };
            score_source.data = {
                insert_times: d.scores.insert_times,
                scores: d.scores.scores,
            };
            view_source.change.emit();
            score_source.change.emit();
        });
}
