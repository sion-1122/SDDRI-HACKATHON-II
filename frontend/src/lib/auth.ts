/**BetterAuth configuration for Next.js 16.

[Task]: T018
[From]: specs/001-user-auth/quickstart.md
*/
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins/jwt";

export const auth = betterAuth({
  database: process.env.DATABASE_URL,
  emailAndPassword: {
    enabled: true,
    disableSignUp: false,
    requireEmailVerification: false,
    minPasswordLength: 8,
    autoSignIn: false,
  },
  plugins: [
    jwt({
      expiresIn: "7d",
      secret: process.env.BETTER_AUTH_SECRET,
    }),
  ],
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
});
