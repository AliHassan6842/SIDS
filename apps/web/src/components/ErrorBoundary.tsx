import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryState { failed: boolean; }

export class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Frontend render failure", { message: error.message, componentStack: info.componentStack });
  }

  render() {
    if (this.state.failed) {
      return (
        <main className="fatal-error">
          <h1>Something went wrong</h1>
          <p>The page could not be displayed. Your camera is no longer in use.</p>
          <button className="button" onClick={() => window.location.reload()}>Reload SIDS</button>
        </main>
      );
    }
    return this.props.children;
  }
}
