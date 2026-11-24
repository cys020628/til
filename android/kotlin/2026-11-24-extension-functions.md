# Kotlin 확장 함수 (Extension Functions)

- 날짜: 2026-11-24
- 분류: android / kotlin

## TODO

- [x] 확장 함수가 왜 필요한지 이해
- [x] 문법과 수신 객체(receiver) 개념 이해
- [x] 규칙 5가지 확인 (멤버 우선, 정적 결정, nullable, 프로퍼티, private 불가)
- [x] Android에서 쓰는 예제 읽어 보기
- [ ] 직접 작성: `Context.toast()`, `View.visible()/gone()`을 내 프로젝트에 적용
- [ ] 다음 주제: 스코프 함수 (`let`, `apply`, `run`, `also`, `with`)

---

## 한 줄 요약

**이미 만들어진 클래스에 내가 만든 함수를 "원래 있던 기능처럼" 붙여 쓰는 문법**

- 클래스 코드를 열어서 고치지 않음
- 상속도 필요 없음
- `"abc".내가만든함수()` 형태로 점(`.`)을 찍어 호출 가능

---

## 1. 왜 필요한가

### 문제 상황

- 문자열의 마지막 글자를 구하고 싶음
- `String` 클래스에는 `lastChar()`라는 기능이 없음
- `String`은 코틀린 표준 라이브러리 클래스라서 내가 코드를 고칠 수 없음

### 기존 방식: 유틸 함수

```kotlin
fun lastChar(s: String): Char = s[s.length - 1]

println(lastChar("Kotlin"))  // n
```

- 동작은 하지만 `lastChar(...)` 안에 값을 넣는 모양이라 읽는 흐름이 어색함
- 함수가 많아지면 `trim(upper(clean(s)))`처럼 안쪽부터 읽어야 함

### 확장 함수 방식

```kotlin
fun String.lastChar(): Char = this[length - 1]

println("Kotlin".lastChar())  // n
```

- `"Kotlin".lastChar()`처럼 **왼쪽에서 오른쪽으로 읽힘**
- 마치 `String`에 원래 있던 기능처럼 보임
- IDE에서 `.`을 찍으면 자동완성 목록에도 나타남

---

## 2. 문법 뜯어보기

```kotlin
fun String.lastChar(): Char = this[length - 1]
//  ①       ②         ③        ④
```

| 번호 | 부분 | 의미 |
|---|---|---|
| ① | `String` | **수신 객체 타입**. 어떤 클래스에 기능을 붙일지 정함 |
| ② | `lastChar` | 새로 만드는 함수 이름 |
| ③ | `Char` | 반환 타입 |
| ④ | `this` | **수신 객체**. 점 앞에 있는 실제 값 (`"Kotlin"`) |

- `this`는 생략 가능함 → `length - 1`만 써도 `this.length - 1`과 같음
- `"Kotlin".lastChar()`를 호출하면 `this`에 `"Kotlin"`이 들어감

### 내부에서는 이렇게 동작함

- 실제로 `String` 클래스에 함수가 끼워지는 것이 **아님**
- 컴파일하면 수신 객체를 첫 번째 인자로 받는 **일반 정적 함수**로 바뀜
- 즉 `"Kotlin".lastChar()`는 사실상 `lastChar("Kotlin")`과 같은 코드
- 겉모양만 점을 찍는 형태로 보이게 해 주는 문법적 편의 기능

> 이 사실 하나를 기억하면 아래 규칙들이 대부분 설명됨

---

## 3. 규칙 5가지

### 규칙 1. 멤버 함수가 항상 이김

클래스 안에 원래 있던 함수와 이름·인자가 같은 확장 함수를 만들면 **원래 함수가 호출됨**

```kotlin
class Person {
    fun hello() = "멤버 함수"
}

fun Person.hello() = "확장 함수"

println(Person().hello())  // "멤버 함수"
```

- 확장 함수는 기존 기능을 덮어쓸 수 없음
- 컴파일러가 "확장 함수가 멤버에 가려짐"이라는 경고를 띄움

### 규칙 2. 어떤 함수를 부를지는 "변수에 적힌 타입"으로 결정됨

```kotlin
open class Shape
class Rect : Shape()

fun Shape.name() = "Shape"
fun Rect.name() = "Rect"

val s: Shape = Rect()   // 실제 값은 Rect, 변수 타입은 Shape
println(s.name())       // "Shape"
```

- 실제 객체가 `Rect`여도 변수 타입이 `Shape`면 `Shape`용 확장 함수가 호출됨
- 일반 멤버 함수의 오버라이드(다형성)와 다르게 동작함
- 이유: 확장 함수는 정적 함수라서 **컴파일할 때** 이미 어떤 함수인지 정해짐

### 규칙 3. nullable 타입에도 붙일 수 있음

```kotlin
fun String?.orDash(): String = if (this.isNullOrEmpty()) "-" else this

val name: String? = null
println(name.orDash())   // "-"
```

- 타입 뒤에 `?`를 붙이면 `null`인 값에도 호출 가능
- 일반 멤버 함수는 `null`에 호출하면 에러(NPE)가 나지만 확장 함수는 가능함
- 함수 안에서 `this`가 `null`인 경우를 직접 처리해야 함
- 참고: 표준 라이브러리의 `isNullOrEmpty()`, `orEmpty()`도 같은 방식의 확장 함수

### 규칙 4. 확장 프로퍼티도 만들 수 있음

```kotlin
val String.lastIndexSafe: Int
    get() = if (isEmpty()) -1 else length - 1
```

- 함수뿐 아니라 `프로퍼티(변수처럼 쓰는 값)`도 확장 가능
- 클래스에 실제 저장 공간(필드)이 생기는 것이 아니라서 값을 저장할 수 없음
- 그래서 `get()`으로 **계산해서 돌려주는 형태만** 가능함 (초기값 대입 불가)

### 규칙 5. private 멤버는 못 건드림

- 확장 함수는 클래스 **밖**에 있는 함수라서 `public`으로 열려 있는 것만 사용 가능
- 클래스 내부의 `private`, `protected` 멤버에는 접근 불가

---

## 4. Android 예제

### 토스트 메시지

```kotlin
fun Context.toast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

// 사용 (Activity 안에서)
toast("저장되었습니다")
```

- `Activity`는 `Context`를 상속하므로 `toast()`를 바로 호출 가능
- 매번 `Toast.makeText(this, ..., ...).show()`를 쓰는 반복을 줄여 줌

### 뷰 보이기 / 숨기기

```kotlin
fun View.visible() { visibility = View.VISIBLE }
fun View.gone() { visibility = View.GONE }

// 사용
binding.progressBar.gone()
binding.resultText.visible()
```

- `visibility = View.GONE`을 매번 쓰는 대신 의미가 드러나는 이름으로 호출 가능
- `TextView`, `Button` 등 모든 `View` 자식 클래스에서 사용 가능

---

## 5. 사용할 때 주의할 점

- 이름이 너무 흔한 확장 함수(`format`, `get` 등)는 다른 함수와 헷갈릴 수 있어서 피하기
- 같은 이름의 확장이 여러 곳에 있으면 `import`에 따라 다른 함수가 호출될 수 있음
- 확장 함수를 남발하면 "이 기능이 원래 클래스 것인지 내가 만든 것인지" 구분이 어려워짐
- 프로젝트 전체에서 쓸 것은 `ext/` 같은 별도 패키지·파일에 모아 두는 편이 찾기 쉬움

---

## 용어 정리

| 용어 | 뜻 |
|---|---|
| 확장 함수 | 기존 클래스에 붙여 쓰는 함수 |
| 수신 객체 (receiver) | 점(`.`) 앞에 오는 값. 함수 안에서 `this`로 접근 |
| 수신 객체 타입 | 함수 이름 앞에 적는 타입 (`String.lastChar`의 `String`) |
| 정적 디스패치 | 어떤 함수를 부를지 컴파일 시점에 정하는 방식 |
| 멤버 함수 | 클래스 안에 원래 정의된 함수 |

---

## 모르는 것 / 내일 이어서

- 멤버 확장 함수(클래스 안에서 다른 클래스를 확장하는 방식)는 언제 쓰는지
- 확장 함수 파일을 어디에 두는 것이 좋은지 (`ext/` 패키지 vs 사용하는 파일 옆)

## 링크

- Kotlin 공식 문서 Extensions: https://kotlinlang.org/docs/extensions.html
