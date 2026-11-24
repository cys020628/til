# Kotlin 확장 함수 (Extension Functions)

- 날짜: 2026-11-24
- 분류: android / kotlin

---

## 1. 일단 하나 만들어 보기

`String`에 마지막 글자를 돌려주는 함수 추가

```kotlin
fun String.lastChar(): Char = this[length - 1]

fun main() {
    println("Kotlin".lastChar())   // n
    println("Android".lastChar())  // d
}
```

- `String.lastChar()` → 앞의 `String`이 **수신 객체 타입** (어떤 클래스에 붙일지)
- 함수 안의 `this` → 점(`.`) 앞에 있는 실제 값
  - `"Kotlin".lastChar()` 호출 시 `this`는 `"Kotlin"`
- `String` 클래스 코드는 건드리지 않았는데 `"Kotlin".lastChar()`처럼 바로 호출 가능

### this는 생략 가능

```kotlin
fun String.lastChar(): Char = this[length - 1]   // this.length 에서 this 생략
fun String.lastChar2(): Char = get(length - 1)   // this.get(...) 에서 this 생략
```

- 클래스 안에서 `this`를 생략하듯 확장 함수 안에서도 생략 가능
- 결과는 동일

### 인자도 받을 수 있음

```kotlin
fun String.repeatWith(sep: String, times: Int): String =
    List(times) { this }.joinToString(sep)

fun main() {
    println("ha".repeatWith("-", 3))   // ha-ha-ha
}
```

- 수신 객체(`this`)와 일반 인자(`sep`, `times`)를 같이 사용
- 호출할 때는 수신 객체는 점 앞에, 인자는 괄호 안에 작성

---

## 2. 정말 클래스에 추가된 걸까?

결론: **추가된 것이 아님**. 컴파일하면 수신 객체를 첫 번째 인자로 받는 일반 정적 함수로 바뀜

```kotlin
// 이렇게 쓴 코드가
"Kotlin".lastChar()

// 사실상 이것과 같은 코드
lastChar("Kotlin")
```

- 점을 찍어서 부르는 모양만 만들어 주는 문법적 편의 기능
- 이 점이 아래 실험 결과들의 이유가 됨

---

## 3. 실험: 원래 있던 함수와 이름이 같으면?

```kotlin
class Person {
    fun hello() = "멤버 함수"
}

fun Person.hello() = "확장 함수"

fun main() {
    println(Person().hello())   // 멤버 함수
}
```

- 결과는 **"멤버 함수"**
- 확장 함수가 만들어져 있어도 클래스 안의 원래 함수가 우선
- IDE에서 `Extension is shadowed by a member` 경고 표시
- 정리: 확장 함수로 기존 기능을 덮어쓰는 것은 불가능

---

## 4. 실험: 부모 타입 변수에 자식 객체를 넣으면?

```kotlin
open class Shape
class Rect : Shape()

fun Shape.name() = "Shape"
fun Rect.name() = "Rect"

fun main() {
    val s: Shape = Rect()      // 실제 객체는 Rect, 변수에 적힌 타입은 Shape
    println(s.name())          // Shape
    println((s as Rect).name()) // Rect
}
```

- `s`의 실제 객체는 `Rect`인데도 **"Shape"** 출력
- 일반 멤버 함수(오버라이드)는 실제 객체 기준으로 호출되지만 확장 함수는 **변수에 적힌 타입** 기준
- 이유: 확장 함수는 정적 함수라서 컴파일할 때 이미 어떤 함수인지 정해짐
- `s as Rect`로 타입을 바꿔서 부르면 `Rect`용 함수가 호출됨

---

## 5. 실험: null일 때도 호출할 수 있을까?

```kotlin
fun String?.orDash(): String = if (this.isNullOrEmpty()) "-" else this

fun main() {
    val name: String? = null
    println(name.orDash())         // -
    println("kotlin".orDash())     // kotlin
    println("".orDash())           // -
}
```

- 수신 객체 타입에 `?`를 붙이면(`String?`) `null`에도 호출 가능
- 비교: 일반 멤버는 `name.length`가 컴파일 에러, `name?.length`로 써야 함
- 확장 함수 안에서는 `this`가 `null`인 경우를 직접 처리해야 함
- `isNullOrEmpty()`, `orEmpty()` 같은 표준 라이브러리 함수도 같은 방식의 확장 함수

---

## 6. 실험: 확장 프로퍼티

```kotlin
val String.lastIndexSafe: Int
    get() = if (isEmpty()) -1 else length - 1

fun main() {
    println("abc".lastIndexSafe)   // 2
    println("".lastIndexSafe)      // -1
}
```

- 함수뿐 아니라 프로퍼티(변수처럼 쓰는 값)도 확장 가능
- 호출할 때 괄호 없이 `"abc".lastIndexSafe`로 사용

### 초기값을 넣어 보면?

```kotlin
val String.count2: Int = 0
// 컴파일 에러: Extension property cannot be initialized because it has no backing field
```

- 클래스에 실제 저장 공간(backing field)이 생기는 것이 아니라서 값 저장 불가
- `get()`으로 계산해서 돌려주는 형태만 가능

---

## 7. 실험: private 멤버에 접근해 보면?

```kotlin
class Account {
    private val balance = 100
    val owner = "kim"
}

fun Account.show() {
    println(owner)     // 가능
    println(balance)   // 컴파일 에러: Cannot access 'balance': it is private in 'Account'
}
```

- 확장 함수는 클래스 **밖**에 있는 함수
- `public`으로 열려 있는 멤버만 사용 가능 (`private`, `protected` 접근 불가)

---

## 8. Android에서 써 보기

### 토스트

```kotlin
fun Context.toast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

// Activity 안에서
toast("저장되었습니다")
```

- `Activity`는 `Context`를 상속하므로 `toast(...)`를 바로 호출 가능
- `Toast.makeText(this, ..., ...).show()` 반복 작성이 사라짐

### 뷰 보이기 / 숨기기

```kotlin
fun View.visible() { visibility = View.VISIBLE }
fun View.gone() { visibility = View.GONE }

// 사용
binding.progressBar.gone()
binding.resultText.visible()
```

- `TextView`, `Button`, `ProgressBar` 등 모든 `View` 자식 클래스에서 사용 가능
- `visibility = View.GONE`보다 의미가 바로 드러나는 이름

---

## 정리: 확인한 규칙

| 번호 | 규칙 | 확인한 실험 |
|---|---|---|
| 1 | 멤버 함수가 확장 함수보다 우선 | 3 |
| 2 | 호출 함수는 변수에 적힌 타입으로 결정 | 4 |
| 3 | nullable 타입에도 붙일 수 있음 | 5 |
| 4 | 확장 프로퍼티는 `get()`만 가능 | 6 |
| 5 | private, protected 멤버 접근 불가 | 7 |

## 주의할 점

- `format`, `get`처럼 흔한 이름은 다른 함수와 헷갈릴 수 있어서 피하기
- 같은 이름의 확장이 여러 곳에 있으면 `import`에 따라 다른 함수가 호출될 수 있음
- 프로젝트 전체에서 쓰는 확장은 `ext/` 같은 별도 패키지·파일에 모으기

## 용어

| 용어 | 뜻 |
|---|---|
| 수신 객체 (receiver) | 점(`.`) 앞에 오는 값. 함수 안에서 `this`로 접근 |
| 수신 객체 타입 | 함수 이름 앞에 적는 타입 (`String.lastChar`의 `String`) |
| 정적 디스패치 | 어떤 함수를 부를지 컴파일 시점에 정하는 방식 |
| 멤버 함수 | 클래스 안에 원래 정의된 함수 |

## 모르는 것 / 내일 이어서

- 멤버 확장 함수(클래스 안에서 다른 클래스를 확장하는 방식)는 언제 쓰는지
- 확장 함수 파일을 어디에 두는 것이 좋은지 (`ext/` 패키지 vs 사용하는 파일 옆)

## 링크

- Kotlin 공식 문서 Extensions: https://kotlinlang.org/docs/extensions.html
