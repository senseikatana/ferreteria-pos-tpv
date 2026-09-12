export default defineNuxtPlugin(async () => {
  const { initKatanaFromCdn } = useKatanaApi()
  await initKatanaFromCdn()
})
