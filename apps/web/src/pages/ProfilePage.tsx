import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { UserProfile } from "../api/contracts";
import { clearToken } from "../auth/tokenStore";
import { ErrorState, LoadingState } from "../components/AsyncState";
import { Icon } from "../components/Icon";
import { PageHeader } from "../components/PageHeader";

export function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [fullName, setFullName] = useState("");
  const [language, setLanguage] = useState("en");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    api.me(controller.signal).then((value) => {
      setProfile(value);
      setFullName(value.fullName);
      setLanguage(value.language || "en");
    }).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Profile could not be loaded.");
    });
    return () => controller.abort();
  }, []);

  const save = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const updated = await api.updateMe({ fullName: fullName.trim(), language });
      setProfile(updated);
      setNotice("Profile saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Profile could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  const logout = () => {
    clearToken();
    navigate("/login", { replace: true });
  };

  return (
    <div className="page">
      <PageHeader title="Profile" />
      {error && !profile ? <ErrorState message={error} /> : !profile ? <LoadingState /> : (
        <>
          <div className="profile-intro"><span><Icon name="profile" /></span><div><strong>{profile.fullName}</strong><small>{profile.email}</small></div></div>
          <form className="form-stack profile-form" onSubmit={save}>
            <label>Full name<input required minLength={2} maxLength={100} value={fullName} onChange={(event) => setFullName(event.target.value)} /></label>
            <label>Email address<input value={profile.email} disabled aria-describedby="email-note" /></label>
            <small id="email-note" className="muted">Contact support to change your sign-in email.</small>
            <label>Language<select value={language} onChange={(event) => setLanguage(event.target.value)}><option value="en">English</option><option value="ur">Urdu</option></select></label>
            {error ? <p className="form-error" role="alert">{error}</p> : null}
            {notice ? <p className="form-success" role="status">{notice}</p> : null}
            <button className="button" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
          </form>
          <button className="button button--outline logout-button" onClick={logout}>Sign out</button>
        </>
      )}
    </div>
  );
}
