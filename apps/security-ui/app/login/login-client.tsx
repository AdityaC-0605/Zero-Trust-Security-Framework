"use client"

import type React from "react"

import { useCallback, useEffect, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { Shield, Lock, Mail, CheckCircle2, Loader2, ArrowRight, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent } from "@/components/ui/card"
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp"
import { exchangeFirebaseIdToken, HttpError } from "@/lib/api"
import { auth, firebaseConfigStatus } from "@/lib/firebase"
import { signInWithEmailAndPassword } from "firebase/auth"
import { useSession } from "@/hooks/use-session"

export default function LoginClient() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { loading: sessionLoading, authenticated, user } = useSession({ redirectToLogin: false })
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: Login, 2: MFA
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [otp, setOtp] = useState("")
  const [error, setError] = useState<string | null>(null)

  const roleHome = (role?: string | null) => {
    if (role === "student") return "/student"
    return "/"
  }

  const getSafeNext = useCallback(
    (role?: string | null) => {
      const next = searchParams?.get("next") || ""
      if (!next) return null
      if (!next.startsWith("/")) return null
      if (next.startsWith("//")) return null
      if (role === "student" && !next.startsWith("/student")) return null
      return next
    },
    [searchParams]
  )

  useEffect(() => {
    if (!sessionLoading && authenticated) {
      const target = getSafeNext(user?.role) || roleHome(user?.role)
      router.replace(target)
    }
  }, [authenticated, getSafeNext, router, sessionLoading, user?.role])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      if (!auth) {
        throw new Error(
          "Firebase is not configured. Set NEXT_PUBLIC_FIREBASE_* env vars in apps/security-ui/.env.local and restart the dev server."
        )
      }
      const cred = await signInWithEmailAndPassword(auth, email, password)
      const idToken = await cred.user.getIdToken()
      const res = await exchangeFirebaseIdToken(idToken)
      const role = (res as any)?.user?.role as string | undefined
      const target = getSafeNext(role) || roleHome(role)
      router.replace(target)
    } catch (err) {
      if (err instanceof HttpError) {
        setError(err.message)
      } else {
        setError(err instanceof Error ? err.message : "Login failed")
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Show Firebase configuration error if not properly set up
  if (!firebaseConfigStatus.hasRealConfig) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-8">
        <Card className="w-full max-w-md bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8">
            <div className="text-center mb-6">
              <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Firebase Configuration Required</h1>
              <p className="text-gray-300">Please set up your Firebase web app configuration</p>
            </div>
            
            <div className="space-y-4 text-sm text-gray-300">
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-400 mb-2">Steps to Fix:</h3>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Go to Firebase Console</li>
                  <li>Get your web app configuration</li>
                  <li>Update apps/security-ui/.env.local</li>
                  <li>Restart the dev server</li>
                </ol>
              </div>
              
              <div className="text-center">
                <p className="text-gray-400">
                  See <code className="bg-gray-800 px-2 py-1 rounded">GET_FIREBASE_CONFIG.md</code> for detailed instructions
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleMFASubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      if (otp.trim().length !== 6) {
        setError("Enter the 6-digit code")
        return
      }
      window.location.href = "/"
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0f172a] flex overflow-hidden">
      {/* Left Side: Animated Background & Security Icons */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col items-center justify-center p-12 overflow-hidden bg-[#0f172a]">
        {/* Animated Gradient Background */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/30 via-transparent to-accent/20 animate-pulse" />
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent/20 blur-[120px]" />
        </div>

        {/* Security Icons */}
        <div className="relative z-10 flex flex-col items-center space-y-8">
          <div className="flex items-center gap-4">
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20">
              <Shield className="w-12 h-12 text-primary" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white">Zero Trust</h1>
              <p className="text-xl text-white/70">Security Framework</p>
            </div>
          </div>

          <div className="space-y-4 max-w-md text-center">
            <h2 className="text-2xl font-semibold text-white">Secure Access Control</h2>
            <p className="text-white/60 leading-relaxed">
              Experience enterprise-grade authentication with multi-factor security, device trust validation, and
              role-based access control.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 w-full max-w-md">
            <div className="p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-primary/20">
                  <Lock className="w-5 h-5 text-primary" />
                </div>
                <span className="text-white font-medium">MFA Protected</span>
              </div>
              <p className="text-white/50 text-sm">Multi-factor authentication for enhanced security</p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-accent/20">
                  <CheckCircle2 className="w-5 h-5 text-accent" />
                </div>
                <span className="text-white font-medium">Device Trust</span>
              </div>
              <p className="text-white/50 text-sm">Continuous device verification and scoring</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side: Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 bg-background relative">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Header */}
          <div className="lg:hidden text-center space-y-4">
            <div className="flex items-center justify-center gap-3">
              <div className="p-3 rounded-xl bg-primary/10">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Zero Trust</h1>
                <p className="text-sm text-muted-foreground">Security Framework</p>
              </div>
            </div>
          </div>

          <Card className="border-border/50 shadow-xl">
            <CardContent className="p-8 space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold">Welcome back</h2>
                <p className="text-muted-foreground">Sign in to access your security dashboard</p>
              </div>

              {error && (
                <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20">
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}

              {step === 1 ? (
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Checkbox id="remember" />
                      <Label htmlFor="remember" className="text-sm">
                        Remember me
                      </Label>
                    </div>
                    <Link href="#" className="text-sm text-primary hover:underline">
                      Forgot password?
                    </Link>
                  </div>

                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                      <span className="flex items-center">
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </span>
                    ) : (
                      <span className="flex items-center">
                        Sign in
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </span>
                    )}
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleMFASubmit} className="space-y-6">
                  <div className="text-center space-y-2">
                    <h3 className="text-lg font-semibold">Two-factor authentication</h3>
                    <p className="text-sm text-muted-foreground">
                      Enter the 6-digit code from your authenticator app
                    </p>
                  </div>

                  <div className="flex justify-center">
                    <InputOTP maxLength={6} value={otp} onChange={setOtp}>
                      <InputOTPGroup>
                        <InputOTPSlot index={0} />
                        <InputOTPSlot index={1} />
                        <InputOTPSlot index={2} />
                        <InputOTPSlot index={3} />
                        <InputOTPSlot index={4} />
                        <InputOTPSlot index={5} />
                      </InputOTPGroup>
                    </InputOTP>
                  </div>

                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                      <span className="flex items-center">
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Verifying...
                      </span>
                    ) : (
                      <span className="flex items-center">
                        Verify
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </span>
                    )}
                  </Button>

                  <Button type="button" variant="ghost" className="w-full" onClick={() => setStep(1)}>
                    Back to login
                  </Button>
                </form>
              )}

              <div className="text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{" "}
                <Link href="/signup" className="text-primary hover:underline">
                  Sign up
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
