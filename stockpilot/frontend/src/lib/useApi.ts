import { useCallback, useEffect, useState } from 'react'

interface ApiState<T> {
  data: T | null
  error: Error | null
  loading: boolean
  /** Fetch again, e.g. after a change was saved. */
  reload: () => void
}

/**
 * Runs `fetcher` whenever `deps` change and tracks loading/error state.
 * Responses from outdated requests are ignored, so fast typing in a search
 * box can't show results for an earlier query.
 */
export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[]): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)
  const [version, setVersion] = useState(0)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(fetcher, deps)

  useEffect(() => {
    let current = true
    setLoading(true)
    setError(null)

    run()
      .then((result) => {
        if (current) setData(result)
      })
      .catch((err: unknown) => {
        if (current) setError(err instanceof Error ? err : new Error(String(err)))
      })
      .finally(() => {
        if (current) setLoading(false)
      })

    return () => {
      current = false
    }
  }, [run, version])

  const reload = useCallback(() => setVersion((v) => v + 1), [])

  return { data, error, loading, reload }
}

/** Returns `value` once it has stopped changing for `delay` ms. */
export function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}
