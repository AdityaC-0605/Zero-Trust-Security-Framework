"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useSession } from "@/hooks/use-session"
import { logout, HttpError } from "@/lib/api"

export default function StudentHomePage() {
  const router = useRouter()
  const { loading, authenticated, user } = useSession({ redirectToLogin: true })
  const [error, setError] = useState<string | null>(null)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  useEffect(() => {
    if (loading) return
    if (!authenticated) return
    if (user?.role && user.role !== "student") {
      router.replace("/")
    }
  }, [authenticated, loading, router, user?.role])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md w-full space-y-4">
        <Card className="bg-card border-border">
          <CardContent className="p-6 space-y-3">
            <div className="text-sm font-semibold">Student Portal</div>
            <div className="text-xs text-muted-foreground">
              Signed in as {user?.email || user?.id || "student"}.
            </div>
            {error && <div className="text-xs text-destructive">{error}</div>}
            <Button
              className="w-full"
              disabled={isLoggingOut}
              onClick={async () => {
                setError(null)
                setIsLoggingOut(true)
                try {
                  await logout()
                  router.replace("/login")
                } catch (e) {
                  setError(e instanceof HttpError ? e.message : "Logout failed")
                } finally {
                  setIsLoggingOut(false)
                }
              }}
            >
              {isLoggingOut ? "Signing out..." : "Sign out"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
