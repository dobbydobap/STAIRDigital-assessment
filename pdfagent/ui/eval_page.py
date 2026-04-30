"""Live evaluation page — runs the 8-query suite and renders pass/fail with traces.

Calls the same `eval.run_eval.run_eval` function the CLI uses.
"""
from __future__ import annotations

import streamlit as st

from pdfagent.ui.theme import pill


def render_eval_page() -> None:
    st.markdown("## Live evaluation suite")
    st.caption(
        "Runs every query in `eval/queries.yaml` against the agent and asserts "
        "the rubric-defined behaviour: citations on every in-scope answer, "
        "verbatim quote verification, and explicit refusals on out-of-scope queries."
    )

    if "eval_report" not in st.session_state:
        st.session_state.eval_report = None

    col1, col2 = st.columns([1, 4])
    with col1:
        run = st.button("Run eval suite", type="primary")
    with col2:
        if st.session_state.eval_report:
            r = st.session_state.eval_report
            passed = r.get("passed", 0)
            total = r.get("total", 0)
            kind = "ok" if passed == total else "fail"
            st.markdown(pill(f"{passed}/{total} passed", kind), unsafe_allow_html=True)

    if run:
        from eval.run_eval import run_eval
        with st.spinner("Running queries…"):
            try:
                report = run_eval()
                st.session_state.eval_report = report
            except Exception as e:
                st.error(f"Eval failed to start: {e}")
                return

    report = st.session_state.eval_report
    if not report:
        st.info("Click **Run eval suite** to execute the 5 in-scope + 3 out-of-scope queries.")
        return

    st.markdown(f"**PDF:** `{report.get('pdf_id', '?')}` · **Sample:** `{report.get('sample_filename', '?')}`")
    for r in report.get("results", []):
        ok = r.get("ok")
        kind = "ok" if ok else "fail"
        title = f"{'PASS' if ok else 'FAIL'} — {r.get('id', '?')}: {r.get('query', '')}"
        with st.expander(title, expanded=not ok):
            st.markdown(pill("expected: " + r.get("expected_behavior", "?"), "info"), unsafe_allow_html=True)
            st.markdown(pill("got: " + r.get("observed", "?"), kind), unsafe_allow_html=True)
            if r.get("notes"):
                st.write(r["notes"])
            ans = r.get("answer", {})
            if ans.get("answer"):
                st.markdown("**Answer:**")
                st.write(ans["answer"])
            if ans.get("refusal_reason"):
                st.markdown("**Refusal reason:**")
                st.write(ans["refusal_reason"])
            cits = ans.get("citations", [])
            if cits:
                st.markdown("**Citations:**")
                for c in cits:
                    st.markdown(
                        f"- p.{c.get('page')} §{c.get('section') or '—'}\n"
                        f"  > {c.get('quoted_span', '')}"
                    )
            v = r.get("verification", {})
            if v:
                vk = "ok" if v.get("ok") else "fail"
                st.markdown("Verification: " + pill("ok" if v.get("ok") else v.get("failure_summary", "fail"), vk),
                            unsafe_allow_html=True)
            lat = r.get("latency_ms", {})
            if lat:
                st.caption(
                    f"latency — rewrite {lat.get('rewrite_ms', 0):.0f}ms · "
                    f"retrieve {lat.get('retrieve_ms', 0):.0f}ms · "
                    f"answer {lat.get('answer_ms', 0):.0f}ms · "
                    f"total {lat.get('total_ms', 0):.0f}ms"
                )
