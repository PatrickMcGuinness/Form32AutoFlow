"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

function WorkbenchContent() {
    const searchParams = useSearchParams();
    const id = searchParams.get("id");
    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [generatedFiles, setGeneratedFiles] = useState([]);

    useEffect(() => {
        if (id) fetchPatient();
        else setLoading(false);
    }, [id]);

    const fetchPatient = async () => {
        try {
            const resp = await fetch(`/api/patients/${id}`);
            if (resp.ok) {
                const data = await resp.json();
                setPatient(data);
            }
        } catch (e) {
            console.error("Fetch failed", e);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateInfo = (field, value) => {
        setPatient({
            ...patient,
            patient_info: {
                ...patient.patient_info,
                [field]: value,
            }
        });
    };

    const handleAddEvaluation = () => {
        const newEval = {
            condition_text: "",
            is_substantial_factor: null,
            diagnosis_codes: ["", "", "", ""]
        };
        setPatient({
            ...patient,
            patient_info: {
                ...patient.patient_info,
                injury_evaluations: [...patient.patient_info.injury_evaluations, newEval]
            }
        });
    };

    const handleUpdateEval = (idx, field, value) => {
        const evals = [...patient.patient_info.injury_evaluations];
        evals[idx] = { ...evals[idx], [field]: value };
        setPatient({
            ...patient,
            patient_info: { ...patient.patient_info, injury_evaluations: evals }
        });
    };

    const handleUpdateCode = (idx, codeIdx, value) => {
        const evals = [...patient.patient_info.injury_evaluations];
        const codes = [...evals[idx].diagnosis_codes];
        codes[codeIdx] = value;
        evals[idx] = { ...evals[idx], diagnosis_codes: codes };
        setPatient({
            ...patient,
            patient_info: { ...patient.patient_info, injury_evaluations: evals }
        });
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const resp = await fetch(`/api/patients/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ patient_info: patient.patient_info }),
            });
            if (resp.ok) {
                // Success feedback could be improved here
            }
        } catch (e) {
            alert("Save failed");
        } finally {
            setSaving(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await handleSave();
            const resp = await fetch(`/api/generate/${id}`, {
                method: "POST"
            });
            if (resp.ok) {
                const data = await resp.json();
                setGeneratedFiles(data.files);
            }
        } catch (e) {
            alert("Generation failed");
        } finally {
            setGenerating(false);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center py-32">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-700 border-t-transparent mb-6"></div>
            <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Loading Patient Record...</p>
        </div>
    );

    if (!id || !patient) return (
        <div className="flex flex-col items-center justify-center py-32">
            <p className="text-red-500 font-bold uppercase tracking-widest text-xs">Error: No Patient ID Provided or Record Not Found</p>
            <Link href="/" className="mt-4 text-blue-700 underline font-bold text-xs uppercase tracking-widest">Back to Dashboard</Link>
        </div>
    );

    const info = patient.patient_info;
    const hasValue = (value) => {
        if (value === null || value === undefined) return false;
        return String(value).trim().length > 0;
    };

    const formatDisplayDate = (value) => {
        if (!hasValue(value)) return null;

        const rawValue = String(value).trim();
        const isoDateMatch = rawValue.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (isoDateMatch) {
            const [, year, month, day] = isoDateMatch;
            return `${month}/${day}/${year}`;
        }

        return rawValue;
    };

    const formatDateRange = (fromDate, toDate) => {
        const from = formatDisplayDate(fromDate);
        const to = formatDisplayDate(toDate);
        if (!from && !to) return null;
        if (from && to) return `From ${from} to ${to}`;
        if (from) return `From ${from}`;
        return `To ${to}`;
    };

    const purposeRows = [
        {
            key: "a",
            label: "A. Maximum medical improvement (MMI)",
            checked: info.purpose_box_a_checked,
            detail: hasValue(info.purpose_mmi_date) ? `Statutory MMI date: ${formatDisplayDate(info.purpose_mmi_date)}` : null,
        },
        {
            key: "b",
            label: "B. Impairment rating (IR)",
            checked: info.purpose_box_b_checked,
            detail: hasValue(info.purpose_ir_mmi_date) ? `MMI date (IR): ${formatDisplayDate(info.purpose_ir_mmi_date)}` : null,
        },
        {
            key: "c",
            label: "C. Extent of injury",
            checked: info.purpose_box_c_checked,
            detail: hasValue(info.extent_of_injury) ? `Description of accident/incident: ${String(info.extent_of_injury).trim()}` : null,
        },
        {
            key: "d",
            label: "D. Disability - direct result",
            checked: info.purpose_box_d_checked,
            detail: formatDateRange(info.purpose_disability_from_date, info.purpose_disability_to_date),
        },
        {
            key: "e",
            label: "E. Return to work",
            checked: info.purpose_box_e_checked,
            detail: formatDateRange(info.purpose_rtw_from_date, info.purpose_rtw_to_date),
        },
        {
            key: "f",
            label: "F. Return to work (supplemental income benefits)",
            checked: info.purpose_box_f_checked,
            detail: formatDateRange(info.purpose_sib_from_date, info.purpose_sib_to_date),
        },
        {
            key: "g",
            label: "G. Other similar issues",
            checked: info.purpose_box_g_checked,
            detail: hasValue(info.purpose_box_g_description) ? `Description of issues: ${String(info.purpose_box_g_description).trim()}` : null,
        },
    ];

    return (
        <div className="fade-in pb-20">
            {/* Workbench Top Bar (Consistency with Dashboard Hero) */}
            <div className="bg-white py-12 mb-12 border-t-8 border-b-8 border-blue-700 shadow-sm">
                <div className="container mx-auto">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div>
                            <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-blue-700 hover:text-blue-800 transition-colors mb-4 uppercase tracking-widest">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12" /><polyline points="12 19 5 12 12 5" /></svg>
                                Dashboard
                            </Link>
                            <h2 className="text-3xl font-bold text-slate-900">Patient Medical Evaluation Workbench</h2>
                            <p className="text-slate-500 mt-2 text-sm font-medium">Case ID: <span className="font-mono text-slate-800 font-bold">{id}</span> • Patient: <span className="font-bold text-blue-700 underline decoration-blue-200 decoration-2 underline-offset-4">{info.patient_name || "New Patient"}</span></p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className={`px-6 py-3 rounded-xl font-bold text-sm bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-all ${saving ? 'opacity-50' : ''}`}
                            >
                                {saving ? "Saving..." : "Save Progress"}
                            </button>
                            <button
                                onClick={handleGenerate}
                                disabled={generating}
                                className={`px-6 py-3 rounded-xl font-bold text-sm bg-blue-700 text-white shadow-lg shadow-blue-500/20 hover:bg-blue-800 transition-all ${generating ? 'opacity-50' : ''}`}
                            >
                                {generating ? "Generating..." : "Finalize Reports"}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="container mx-auto">
                <div className="grid grid-cols-12 gap-8">
                    {/* LEFT SIDE: Patient Profile (1/3rd) */}
                    <div className="col-span-12 md:col-span-4 flex flex-col gap-10">
                        <section className="card border-slate-200 bg-white">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="h-10 w-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-700"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                                </div>
                                <h3 className="text-lg font-bold text-slate-900">Patient Profile</h3>
                            </div>

                            <div className="space-y-6">
                                <div className="form-group mb-0">
                                    <label className="label text-[11px]">Full Name</label>
                                    <input
                                        className="input text-sm"
                                        value={info.patient_name || ""}
                                        onChange={(e) => handleUpdateInfo('patient_name', e.target.value)}
                                        placeholder="Enter patient name"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="form-group mb-0">
                                        <label className="label text-[11px] mt-1-5">Exam Date</label>
                                        <input
                                            className="input text-sm"
                                            value={info.exam_date || ""}
                                            onChange={(e) => handleUpdateInfo('exam_date', e.target.value)}
                                            placeholder="MM/DD/YYYY"
                                        />
                                    </div>
                                    <div className="form-group mb-0">
                                        <label className="label text-[11px] mt-1-5">Date of Injury</label>
                                        <input
                                            className="input text-sm"
                                            value={info.date_of_injury || ""}
                                            onChange={(e) => handleUpdateInfo('date_of_injury', e.target.value)}
                                            placeholder="MM/DD/YYYY"
                                        />
                                    </div>
                                </div>
                                <div className="form-group mb-0">
                                    <label className="label text-[11px] mt-1-5">Claim Number</label>
                                    <input
                                        className="input text-sm"
                                        value={info.claim_number || ""}
                                        onChange={(e) => handleUpdateInfo('claim_number', e.target.value)}
                                        placeholder="Enter claim ID"
                                    />
                                </div>
                                <div className="form-group mb-0">
                                    <label className="label text-[11px] mt-1-5">Exam Location</label>
                                    <input
                                        className="input text-sm"
                                        value={info.exam_location || ""}
                                        onChange={(e) => handleUpdateInfo('exam_location', e.target.value)}
                                        placeholder="Clinic or Hospital name"
                                    />
                                </div>
                            </div>
                        </section>

                        {generatedFiles.length > 0 && (
                            <section className="card border-emerald-100 bg-emerald-50/20 scale-in mt-2">
                                <h3 className="text-emerald-800 text-sm font-bold mb-6 flex items-center gap-2">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
                                    Generated Reports
                                </h3>
                                <div className="space-y-2">
                                    {generatedFiles.map((file, i) => (
                                        <a
                                            key={i}
                                            href={`/api/download?path=${encodeURIComponent(file.path)}`}
                                            className="flex items-center justify-between p-3 rounded-xl bg-white border border-emerald-100 hover:border-emerald-300 hover:shadow-md transition-all text-xs font-bold text-emerald-700 group"
                                        >
                                            <span className="truncate">{file.type}</span>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:translate-y-0.5 transition-transform"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                                        </a>
                                    ))}
                                </div>
                            </section>
                        )}
                    </div>

                    {/* RIGHT SIDE: Doctor's Evaluation (2/3rds) */}
                    <div className="col-span-12 md:col-span-8">
                        <section className="card shadow-md bg-white border-slate-200">
                            <div className="mb-10 border-b border-slate-100 pb-6">
                                <h3 className="text-2xl font-bold text-slate-900 mb-2">Doctor&apos;s Evaluation</h3>
                                <p className="text-slate-500 max-w-2xl text-sm leading-relaxed">
                                    Identify and evaluate additional claimed diagnoses. Determine if the compensable injury was a
                                    <span className="font-bold text-slate-700"> substantial factor</span> in bringing about these conditions.
                                </p>
                            </div>

                            <div className="space-y-8">
                                <div className="p-6 rounded-2xl border border-slate-200 bg-slate-50/30">
                                    <div className="flex items-center justify-between mb-6">
                                        <span className="px-3 py-1 rounded-full bg-white border border-slate-200 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Purpose of Examination (Part 5)</span>
                                        <div className="h-px flex-grow mx-4 bg-slate-200"></div>
                                    </div>

                                    <div className="space-y-3">
                                        {purposeRows.map((row) => (
                                            <div key={row.key} className="rounded-xl border border-slate-200 bg-white p-3">
                                                <label className="flex items-start gap-3">
                                                    <input
                                                        type="checkbox"
                                                        className="mt-0.5 h-4 w-4 rounded border-slate-300 text-blue-700 focus:ring-blue-700"
                                                        checked={Boolean(row.checked)}
                                                        disabled
                                                        readOnly
                                                    />
                                                    <span className="text-sm font-semibold text-slate-800 leading-snug">
                                                        {row.label}
                                                    </span>
                                                </label>
                                                {row.detail && (
                                                    <p className="mt-2 pl-7 text-xs text-slate-600 leading-relaxed">{row.detail}</p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {info.injury_evaluations.map((evalItem, idx) => (
                                    <div key={idx} className="p-6 rounded-2xl border border-slate-200 bg-slate-50/30 hover:shadow-sm transition-shadow">
                                        <div className="flex items-center justify-between mb-6">
                                            <span className="px-3 py-1 rounded-full bg-white border border-slate-200 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Condition #{idx + 1}</span>
                                            <div className="h-px flex-grow mx-4 bg-slate-200"></div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="space-y-2">
                                                <label className="label text-[11px]">Diagnosis / Condition Description</label>
                                                <textarea
                                                    className="input min-h-[140px] resize-none leading-relaxed text-sm bg-white"
                                                    placeholder="Example: Lumbar disc herniation with radiculopathy..."
                                                    value={evalItem.condition_text}
                                                    onChange={(e) => handleUpdateEval(idx, 'condition_text', e.target.value)}
                                                />
                                            </div>

                                            <div className="space-y-6">
                                                <div>
                                                    <label className="label text-[11px]">Substantial Factor?</label>
                                                    <div className="flex gap-3">
                                                        <button
                                                            onClick={() => handleUpdateEval(idx, 'is_substantial_factor', true)}
                                                            className={`flex-1 py-4 text-sm font-bold rounded-xl border-2 transition-all ${evalItem.is_substantial_factor === true ? 'bg-emerald-600 border-emerald-700 text-white shadow-lg shadow-emerald-600/20' : 'bg-white border-slate-200 text-slate-400 hover:border-slate-300'}`}
                                                        >
                                                            YES
                                                        </button>
                                                        <button
                                                            onClick={() => handleUpdateEval(idx, 'is_substantial_factor', false)}
                                                            className={`flex-1 py-4 text-sm font-bold rounded-xl border-2 transition-all ${evalItem.is_substantial_factor === false ? 'bg-red-600 border-red-700 text-white shadow-lg shadow-red-600/20' : 'bg-white border-slate-200 text-slate-400 hover:border-slate-300'}`}
                                                        >
                                                            NO
                                                        </button>
                                                    </div>
                                                </div>

                                                <div>
                                                    <label className="label text-[11px]">ICD-10 Diagnosis Codes</label>
                                                    <div className="grid grid-cols-4 gap-2">
                                                        {[0, 1, 2, 3].map(cIdx => (
                                                            <input
                                                                key={cIdx}
                                                                className="input text-center px-1 font-mono uppercase font-bold text-sm bg-white"
                                                                placeholder={`#${cIdx + 1}`}
                                                                value={evalItem.diagnosis_codes[cIdx] || ""}
                                                                onChange={(e) => handleUpdateCode(idx, cIdx, e.target.value)}
                                                            />
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                <button
                                    onClick={handleAddEvaluation}
                                    className="w-full py-6 rounded-2xl border-2 border-dashed border-slate-300 bg-white flex flex-col items-center justify-center gap-2 group hover:bg-blue-50 hover:border-blue-200 transition-all"
                                >
                                    <div className="h-10 w-10 rounded-full bg-slate-50 flex items-center justify-center group-hover:scale-110 transition-transform">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-700"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
                                    </div>
                                    <span className="text-xs uppercase tracking-[0.2em] font-bold text-slate-500 group-hover:text-blue-700">Add Diagnosis Condition</span>
                                </button>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function Workbench() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <WorkbenchContent />
        </Suspense>
    );
}
