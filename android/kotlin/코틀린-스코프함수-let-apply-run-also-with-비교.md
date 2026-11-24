# 코틀린 스코프 함수: let, apply, run, also, with 비교 (Scope Functions)

---

## 1. 한눈에 비교

| 함수 | 객체 접근 | 반환값 | 확장 함수 | 주로 쓰는 곳 |
|---|---|---|---|---|
| `let` | `it` | 람다의 결과 | O | null이 아닐 때 실행, 값 변환 |
| `run` | `this` | 람다의 결과 | O | 객체를 설정한 뒤 결과 계산 |
| `with` | `this` | 람다의 결과 | **X** (일반 함수) | 한 객체의 함수를 여러 번 호출 |
| `apply` | `this` | **객체 자신** | O | 객체 생성 직후 설정 |
| `also` | `it` | **객체 자신** | O | 로그, 검증 같은 부가 작업 |

- 구분 기준은 두 가지
  - 객체를 `it`으로 받는가, `this`로 받는가
  - 객체 자신을 돌려주는가, 람다의 마지막 줄 결과를 돌려주는가

---

## 2. 선언 모양

```
fun <T, R> T.let(block: (T) -> R): R
fun <T, R> T.run(block: T.() -> R): R
fun <T, R> with(receiver: T, block: T.() -> R): R
fun <T> T.apply(block: T.() -> Unit): T
fun <T> T.also(block: (T) -> Unit): T
```

- `(T) -> R` 람다 → 객체가 **인자**로 들어와서 `it`
- `T.() -> R` 람다 → 객체가 **수신 객체**라서 `this` (확장 함수 응용편 4번)
- 반환 타입이 `R`이면 람다의 마지막 줄, `T`이면 객체 자신

---

## 3. 하나씩 실행해 보기

### let: `it`으로 받고 결과를 반환

```kotlin
fun main() {
    val name: String? = "kotlin"
    println(name?.let { it.uppercase() })   // KOTLIN

    val none: String? = null
    println(none?.let { it.uppercase() })   // null (람다가 실행되지 않음)
}
```

- `?.let { }` → 값이 `null`이 아닐 때만 실행

### run: `this`로 받고 결과를 반환

```kotlin
class Config {
    var host = ""
    var port = 0
}

fun main() {
    val url = Config().run {
        host = "kotl.in"
        port = 443
        "$host:$port"          // 마지막 줄이 반환값
    }
    println(url)   // kotl.in:443
}
```

### with: 객체를 인자로 넘기고 `this`로 사용

```kotlin
fun main() {
    val result = with(StringBuilder()) {
        append("Hello")
        append(" ")
        append("World")
        toString()             // 마지막 줄이 반환값
    }
    println(result)   // Hello World
}
```

- `StringBuilder().with { }`가 아니라 `with(StringBuilder()) { }` 형태
- 확장 함수가 아니라서 점(`.`)으로 부르지 않음

### apply: `this`로 받고 객체 자신을 반환

```kotlin
class User {
    var name = ""
    var age = 0
}

fun main() {
    val user = User().apply {
        name = "kim"
        age = 20
    }
    println("${user.name} ${user.age}")   // kim 20
}
```

- 생성과 설정을 한 번에 작성 → 변수에 바로 대입 가능

### also: `it`으로 받고 객체 자신을 반환

```kotlin
fun main() {
    val nums = mutableListOf(1, 2, 3)
        .also { println("before: $it") }   // before: [1, 2, 3]
        .apply { add(4) }
    println(nums)   // [1, 2, 3, 4]
}
```

- 체인 중간에 끼워 넣어도 값이 바뀌지 않음 → 로그 확인용으로 적합

---

## 4. 어떤 걸 쓸지 고르는 기준

| 하고 싶은 것 | 사용 |
|---|---|
| null이 아닐 때만 실행 | `?.let { }` |
| 객체 만들면서 설정 | `apply { }` |
| 체인 중간에 로그·검증 | `also { }` |
| 객체를 설정하고 결과 값 계산 | `run { }` |
| 한 객체의 함수를 여러 번 호출 | `with(obj) { }` |

- 객체 자신이 필요하면 `apply`, `also`
- 계산한 결과가 필요하면 `let`, `run`, `with`
- 람다 안의 `it` 이름은 바꿀 수 있음 → `name?.let { n -> n.uppercase() }`
- `this`는 생략 가능하지만 바깥 변수와 이름이 겹치면 헷갈리므로 주의

---

## 5. Android에서 쓰는 모양

```kotlin
// apply: 객체 생성 + 설정
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("id", 1)
}

// let: null이 아닐 때만 실행
user?.let { binding.nameText.text = it.name }

// also: 결과를 바꾸지 않고 로그만 남김
val items = repository.load().also { Log.d("TAG", "loaded: $it") }

// with: binding 여러 개를 한 번에 설정
with(binding) {
    titleText.text = "제목"
    progressBar.isVisible = false
}
```

---

## 6. 확장 함수와의 관계

- `let`, `run`, `apply`, `also`는 **모든 타입 `T`에 붙는 제네릭 확장 함수**
- `with`는 확장 함수가 아니라 일반 함수
- `this`로 받는 함수(`run`, `with`, `apply`)는 "수신 객체가 있는 함수 타입" 사용
- 자세한 개념은 [코틀린-확장함수-응용문법.md](코틀린-확장함수-응용문법.md) 4번 참고

## 참고 자료

- Kotlin 공식 문서, Scope functions: https://kotlinlang.org/docs/scope-functions.html
- 표준 함수 치트시트: https://github.com/JoseAlcerreca/kotlin-std-fun
- 검증: `fun main()`이 있는 예제는 Kotlin 2.4.21(JVM)에서 실행해 주석과 일치 확인, Android 코드는 제외
