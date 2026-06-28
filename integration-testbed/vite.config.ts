export default defineConfig({
  plugins: [react()],
  root: 'src',
  server: {
    port: 3000,
    open: true, // 로컬에서 자동 실행되도록 설정
  },
});
