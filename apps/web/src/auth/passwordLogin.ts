import { setToken } from "./tokenStore";

export const passwordLogin = async (email: string, password: string): Promise<void> => {
  const res = await fetch("/api/Auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Email: email, Password: password }),
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = await res.json();
  if (data?.token) setToken(data.token);
  else throw new Error("No token received");
};
