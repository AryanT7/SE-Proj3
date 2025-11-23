"use client";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import Link from "next/link";
import Navbar from "../components/Navbar";
import Cookies from 'js-cookie';

export default function LoginPage() {
  const router = useRouter();

  /**
   * submits form data
   * @param e user and pass to login
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const formElements: any = e.target;

    try {
      let response = await fetch("http://localhost:5000/api/users/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formElements.login_email.value,
          password: formElements.login_password.value
        }),
        credentials: "include"
      });

      if (!response.ok) {
        // If server responds with 400/500 code, get the specific message
        const errorData = await response.json();
        throw new Error(errorData.message || response.statusText);
      }

      let rj = await response.json();
      console.log(rj);

      // Success path:
      Cookies.set('user_id', rj.user_id, {
        expires: 1
      });

      window.location.href = "/";

    } catch (error: unknown) {
      // This catches network errors AND the error thrown above
      console.error(error);
      alert("Error: " + (error instanceof Error ? error.message : String(error)));
    }

  };

  return (
    <section className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-2">Log In</h1>
      <p className="text-sm text-gray-600 mb-6">Sign in to start ordering delicious snacks.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="login_email"
            required
            autoComplete="email"
            className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="login_password"
            autoComplete="current-password"
            required
            className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          className="w-full rounded-xl bg-black px-5 py-2.5 text-sm text-white hover:bg-gray-800 transition"
        >
          Log In
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-gray-600">
        Don&apos;t have an account?{" "}
        <Link href="/signup" className="font-medium text-black underline">
          Sign up
        </Link>
      </p>
    </section>
  );
}
