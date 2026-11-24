# Kotlin 확장 함수 (Extension Functions)

- 날짜: 2026-11-24
- 분류: android / kotlin

## TODO

- [x] 확장 함수 문법과 수신 객체(receiver) 이해
- [x] 정적 디스패치(멤버가 우선, 오버라이드 불가) 확인
- [x] nullable 수신 객체와 확장 프로퍼티 정리
- [x] Android에서 쓰는 예제 만들어 보기
- [ ] 직접 작성: `Context.toast()`, `View.visible()/gone()`을 프로젝트에 적용
- [ ] 이어서: 스코프 함수(`let`, `apply`, `run`, `also`, `with`)

## 정리

클래스를 상속하거나 수정하지 않고 기존 클래스에 함수를 추가한 것처럼 호출할 수 있게 해 주는 기능입니다.

```kotlin
fun String.lastChar(): Char = this[length - 1]

println("Kotlin".lastChar())  // n
```

- `String.`이 수신 객체 타입, 함수 안에서 `this`가 수신 객체입니다.
- 실제로는 클래스에 멤버가 추가되는 것이 아니라, 수신 객체를 첫 번째 인자로 받는 **정적 함수**로 컴파일됩니다.

### 1. 확장은 정적으로 결정된다

호출할 함수는 런타임 타입이 아니라 **선언된 타입**으로 정해집니다. 그래서 오버라이드되지 않습니다.

```kotlin
open class Shape
class Rect : Shape()

fun Shape.name() = "Shape"
fun Rect.name() = "Rect"

val s: Shape = Rect()
println(s.name())  // "Shape" (런타임 타입이 Rect여도)
```

### 2. 멤버 함수가 항상 이긴다

같은 시그니처의 멤버 함수와 확장 함수가 있으면 멤버가 호출됩니다. 확장은 멤버를 가릴 수 없습니다.

### 3. nullable 수신 객체

수신 객체 타입을 nullable로 선언하면 `null`에서도 호출할 수 있습니다. 함수 안에서 `this == null`을 직접 처리해야 합니다.

```kotlin
fun String?.orDash(): String = if (this.isNullOrEmpty()) "-" else this

val name: String? = null
println(name.orDash())  // "-"
```

### 4. 확장 프로퍼티

실제 필드가 없으므로 backing field를 쓸 수 없고, `get()`만 정의할 수 있습니다.

```kotlin
val String.lastIndexSafe: Int
    get() = if (isEmpty()) -1 else length - 1
```

### 5. 한계

- 클래스의 `private`, `protected` 멤버에는 접근할 수 없습니다. 공개된 API만 사용할 수 있습니다.
- 이름이 겹치는 확장이 여러 개면 어떤 `import`가 적용되는지 헷갈릴 수 있습니다. 범용 이름(`format`, `get` 등)은 피합니다.

## Android 예제

```kotlin
fun Context.toast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

fun View.visible() { visibility = View.VISIBLE }
fun View.gone() { visibility = View.GONE }

// 사용
toast("저장되었습니다")
binding.progressBar.gone()
```

## 모르는 것 / 내일 이어서

- 멤버 확장 함수(클래스 안에서 다른 클래스를 확장)는 언제 쓰는가?
- 확장 함수를 어디에 모아 두는 것이 좋은가? (`ext/` 패키지 vs 사용하는 파일)

## 링크

- Kotlin 공식 문서: Extensions — https://kotlinlang.org/docs/extensions.html
