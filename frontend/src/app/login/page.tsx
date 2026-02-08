/* Login page (server component).

[Task]: T031, T075
[From]: specs/001-user-auth/plan.md, specs/005-ux-improvement/tasks.md

Updated with Notion-inspired minimalistic design using theme variables.
*/
import { LoginForm } from "@/components/auth/LoginForm";
import { cn } from "@/lib/utils";

export const metadata = {
  title: "Sign In - Todo List",
  description: "Sign in to your Todo List account",
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-[95vw] sm:max-w-[480px] md:max-w-[600px] lg:max-w-[700px] xl:max-w-[800px]">
        {/* Notion-inspired header - clean and minimal */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-foreground tracking-tight mb-2">
            Welcome back
          </h1>
          <p className="text-sm text-muted-foreground">
            Or{" "}
            <a
              href="/register"
              className="font-medium text-foreground hover:text-primary transition-colors underline-offset-4 hover:underline"
            >
              create a new account
            </a>
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}