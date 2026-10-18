import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { getToken, setToken } from "../auth/tokenStore";
import { Icon } from "../components/Icon";

export function RegisterPage() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (getToken()) return <Navigate to="/home" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      const response = await api.register(fullName.trim(), email.trim(), password);
      setToken(response.token);
      navigate("/home", { replace: true });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="register-title">
        <div className="brand brand--centered"><span className="brand__mark"><Icon name="leaf" /></span><span><strong>SIDS</strong><small>Smart Insect Detection</small></span></div>
        <div className="auth-card__intro"><h1 id="register-title">Create your account</h1><p>Save your insect identifications securely in one scan history.</p></div>
        <form onSubmit={submit} className="form-stack">
          <label>Full name<input autoComplete="name" required minLength={2} maxLength={100} value={fullName} onChange={(event) => setFullName(event.target.value)} /></label>
          <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          <label>Password<input type="password" autoComplete="new-password" required minLength={10} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          <label>Confirm password<input type="password" autoComplete="new-password" required minLength={10} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} /></label>
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <button className="button" type="submit" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button>
        </form>
        <p className="auth-card__footer">Already registered? <Link to="/login">Sign in</Link></p>
      </section>
    </main>
  );
}
