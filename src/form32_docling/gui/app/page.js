"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await fetch("/api/patients");
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      }
    } catch (error) {
      console.error("Failed to fetch patients:", error);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadError(null);
    }
  };

  const handleProcessUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        window.location.href = `/workbench/?id=${result.id}`;
      } else {
        const error = await response.json();
        setUploadError(error.detail || "Upload failed");
      }
    } catch (error) {
      setUploadError("Server connection failed. Ensure FastAPI is running.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeletePatient = async (id, name) => {
    if (!confirm(`Are you sure you want to delete patient record for "${name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/patients/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setPatients(patients.filter(p => p.id !== id));
      } else {
        const error = await response.json();
        alert(`Failed to delete: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Delete failed:", error);
      alert("Failed to connect to server.");
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to delete ALL patient sessions? This cannot be undone.")) {
      return;
    }

    try {
      const response = await fetch("/api/patients", {
        method: "DELETE",
      });

      if (response.ok) {
        setPatients([]);
      } else {
        const error = await response.json();
        alert(`Failed to clear database: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Clear all failed:", error);
      alert("Failed to connect to server.");
    }
  };

  return (
    <div className="fade-in">
      <section className="bg-white py-12 mb-12 border-t-8 border-b-8 border-blue-700 shadow-sm">
        <div className="container mx-auto">
          <div className="relative overflow-hidden py-4">
            <div className="relative z-10 max-w-3xl">
              <h2 className="text-4xl font-bold mb-4 tracking-tight text-blue-700">Patient Review Dashboard</h2>
              <p className="text-lg text-slate-600 mb-10 leading-relaxed font-medium">
                Upload New Exam Order Letters (Form 32) to begin the professional disability review process.
                Our system automatically extracts data to populate DWC 068, 069, and 073 forms.
              </p>

              <div className="flex flex-col gap-6">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="relative">
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      disabled={isUploading}
                    />
                    <label
                      htmlFor="file-upload"
                      className={`btn px-6 py-4 text-sm font-bold transition-all shadow-sm ${selectedFile ? 'bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200' : 'bg-blue-700 text-white hover:bg-blue-800'}`}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
                      {selectedFile ? 'Change File' : 'Choose Form DWC032'}
                    </label>
                  </div>

                  {selectedFile && !isUploading && (
                    <button
                      onClick={handleProcessUpload}
                      className="btn bg-blue-500 text-white px-8 py-4 text-sm font-bold shadow-xl shadow-blue-500/20 hover:bg-blue-600 scale-in"
                    >
                      Process Form DWC032
                    </button>
                  )}

                  {isUploading && (
                    <div className="flex items-center gap-3 px-6 py-4 text-blue-800 font-bold bg-blue-50 rounded-xl border border-blue-200 scale-in">
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-700 border-t-transparent"></div>
                      Processing Form DWC032...
                    </div>
                  )}
                </div>

                {selectedFile && !isUploading && (
                  <div className="flex items-center gap-2 text-sm text-blue-100 font-medium scale-in opacity-80">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-300"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="12" y1="18" x2="12" y2="12" /><line x1="9" y1="15" x2="15" y2="15" /></svg>
                    Selected: <span className="text-white font-bold border-b border-blue-400/50 pb-0.5">{selectedFile.name}</span>
                  </div>
                )}
              </div>

              {uploadError && (
                <div className="mt-8 rounded-xl bg-red-500/10 p-4 text-sm text-red-100 border border-red-500/20 flex items-center gap-3 scale-in">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
                  <span className="font-semibold">{uploadError}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <div className="container mx-auto pb-20">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-xl font-bold text-slate-800">Recent Assessments</h3>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{patients.length} Records</span>
        </div>

        <div className="grid-cols-dynamic">
          {isUploading ? (
            <div className="col-span-12 py-16 text-center rounded-3xl border-2 border-blue-100 bg-blue-50/40">
              <div className="mx-auto mb-5 h-12 w-12 animate-spin rounded-full border-4 border-blue-700 border-t-transparent"></div>
              <h4 className="text-xl font-bold text-blue-800 mb-2">Processing in Progress</h4>
              <p className="text-slate-600 max-w-lg mx-auto">
                Extracting fields from Form 32 and preparing your patient record. This can take a moment.
              </p>
            </div>
          ) : patients.length === 0 ? (
            <div className="col-span-12 py-24 text-center glass rounded-3xl border-dashed border-2 border-slate-200">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-white text-slate-300 shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
              </div>
              <h4 className="text-xl font-bold text-slate-800 mb-2">No Assessments Found</h4>
              <p className="text-slate-500 max-w-sm mx-auto">Upload an exam order letter (Form 32) to start generating your workers comp reports.</p>
            </div>
          ) : (
            patients.map((patient) => (
              <div key={patient.id} className="card group hover:-translate-y-1 flex flex-col scale-in">
                <div className="mb-6 flex items-start justify-between">
                  <div className="flex-grow">
                    <h4 className="text-xl font-bold hover:text-blue-700 transition-colors mb-2 cursor-pointer">{patient.name}</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
                        <div className="w-8 flex justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
                        </div>
                        {patient.date || "Date N/A"}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
                        <div className="w-8 flex justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></svg>
                        </div>
                        <span className="truncate max-w-[180px]">{patient.location || "Location N/A"}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-3">
                    <span className={`badge ${patient.status === 'generated' ? 'badge-success' :
                      patient.status === 'pending' ? 'badge-warning' : 'badge-info'
                      }`}>
                      {patient.status}
                    </span>
                    <button
                      onClick={() => handleDeletePatient(patient.id, patient.name)}
                      className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                      title="Delete Record"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /></svg>
                    </button>
                  </div>
                </div>

                <div className="mt-auto pt-6 border-t border-slate-50 flex items-center justify-between">
                  <div className="flex items-center gap-1.5" title="Measurement ID">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">ID {patient.id}</span>
                  </div>
                  <Link href={`/workbench/?id=${patient.id}`} className="btn btn-secondary py-2 px-4 text-xs">
                    Open Workbench
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>

        {patients.length > 0 && !isUploading && (
          <div className="mt-16 pt-8 border-t border-slate-200 flex justify-center">
            <button
              onClick={handleClearAll}
              className="btn text-red-500 text-xs font-bold uppercase tracking-widest hover:text-red-700 transition-colors flex items-center gap-2 px-6 py-3 rounded-xl hover:bg-red-50 shadow-sm border border-red-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /></svg>
              Clear Assessment Archive
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
