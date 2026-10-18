import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { getToken, setToken } from "../auth/tokenStore";
import { Icon } from "../components/Icon";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (getToken()) return <Navigate to="/home" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const response = await api.login(email.trim(), password);
      setToken(response.token);
      navigate("/home", { replace: true });
    } catch (reason) {
      setError(reason instanceof ApiError && reason.status === 401 ? "Email or password is incorrect." : reason instanceof Error ? reason.message : "Sign in failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="login-title">
        <div className="brand brand--centered">
          <span className="brand__mark"><Icon name="leaf" /></span>
          <span><strong>SIDS</strong><small>Smart Insect Detection</small></span>
        </div>
        <div className="auth-card__intro">
          <h1 id="login-title">Welcome back</h1>
          <p>Sign in to identify supported crop insects and view your scan history.</p>
        </div>
        <form onSubmit={submit} className="form-stack">
          <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          <label>Password<input type="password" autoComplete="current-password" minLength={10} required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <button className="button" type="submit" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button>
        </form>
        <p className="auth-card__footer">New to SIDS? <Link to="/register">Create an account</Link></p>
      </section>
    </main>
  );
}
