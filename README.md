# Wizard-game
Shoot game 
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using Microsoft.Xna.Framework.Media;
using System;
using System.Collections.Generic;

namespace Wizard_of_Wizards
{
    public class GameWorld : Game
    {
        private GraphicsDeviceManager graphics; //Premade
        private SpriteBatch spriteBatch;
        public static float gameScale = 0.6f; //We make screensize for game 
        public static float scaleOffset = 0.1f; // It's scale offset for game
        public static Vector2 screenSize; //Essential variables. (screensize is used to adjust various items)
        private Texture2D collisionTexture;
        private Texture2D map;    //It's for Texture2D background
        private SpriteFont text; //A single spritefront for the text (viewing score)
        public static int lives = 3; //We make static field for life
        public static int score;      //Static field for score
        private int highScore;        //Create field for highScore
        public static float speed;      //Make speed field
        private static bool start = false; //startmenu stuff
        public static bool sound = false; //Play soundeffects and music.
        private bool soundTap = true; //Used to prevent music spam.
        private Random random = new Random();

        private List<GameObject> gameObjects;        //List for all gameobjects
        private static List<GameObject> newObjects;  //List for new objects
        private static List<GameObject> deleteObjects; //List for delete objects

        Player player = new Player();   //We need just one player

        /// <summary>
        /// Gameworlds constructor
        /// </summary>
        public GameWorld()
        {
            graphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            IsMouseVisible = true;

            screenSize = new Vector2(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight);
        }
        /// <summary>
        /// Initialize methode
        /// </summary>
        protected override void Initialize()
        {
            GameScale();                                //We make here our screensize

            gameObjects = new List<GameObject>();
            newObjects = new List<GameObject>();
            deleteObjects = new List<GameObject>();

            gameObjects.Add(player);
            gameObjects.Add(new MonsterEnemy(player));//we need to add it for at move into player
            gameObjects.Add(new KnightEnemy(player));//we need to add it for at move into player
            gameObjects.Add(new KnightEnemyRightSide(player));//we need to add it for at move into player


            base.Initialize();
        }
        /// <summary>
        /// Method where we load our content
        /// </summary>
        protected override void LoadContent()
        {
            //Create a new SpriteBatch, which can be used to draw textures.
            spriteBatch = new SpriteBatch(GraphicsDevice);
            map = Content.Load<Texture2D>("map");  // Download background picture for our game
            collisionTexture = Content.Load<Texture2D>("CollisionTexture"); //Download collision texture
            text = Content.Load<SpriteFont>("File"); //Download sprite fond
            MediaPlayer.IsRepeating = true;          //Set MediaPlayer to true
            Song music = Content.Load<Song>("Background"); //Download music
            MediaPlayer.Play(music);                       //Create a MediaPlayer to play downloaded music
            MediaPlayer.Pause();                           //Start, and pause music. Toggable later in the code.

            //Create foreach loop for all GameObjects
            foreach (GameObject go in gameObjects)
            {
                go.LoadContent(Content);
            }
        }
        /// <summary>
        /// Method where we make our updates
        /// </summary>
        /// <param name="gameTime"></param>
        protected override void Update(GameTime gameTime)
        {   //Make here option to start game when we push Key B
            if (!start)
            {
                KeyboardState keyState = Keyboard.GetState();
                if (keyState.IsKeyDown(Keys.B))
                {
                    start = true;
                }
            }
            else
            {
                if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed || Keyboard.GetState().IsKeyDown(Keys.Escape))
                    Exit();
                gameObjects.AddRange(newObjects);
                newObjects.Clear();

                foreach (GameObject go in gameObjects)  //Main update loop
                {
                    go.Update(gameTime);//Call each subclasses' update method, wherein they call for Move and all sorts methods
                    foreach (GameObject item in gameObjects)//Collision checking loop
                    {
                        go.CheckCollision(item);
                    }
                }
                foreach (GameObject go in newObjects) //Add the new objects from AddObject method
                {
                    go.LoadContent(Content);
                    gameObjects.Add(go);
                }
                newObjects.Clear();
                foreach (GameObject go in deleteObjects)//Loop for delete objects on collision
                {
                    gameObjects.Remove(go);
                }
                deleteObjects.Clear();

                KeyboardState keyState = Keyboard.GetState();

                if (keyState.IsKeyDown(Keys.V) && soundTap == true) //Toggle music and sounds
                {
                    if (sound == false)
                    {
                        sound = true;
                    }
                    else
                    {
                        sound = false;
                    }
                    soundTap = false;

                    if (sound)
                    {
                        MediaPlayer.Resume(); //if sound on, resume playing
                    }
                    else
                    {
                        MediaPlayer.Pause(); //if off stop playing
                    }
                }
                if (keyState.IsKeyUp(Keys.V))
                {
                    soundTap = true; //prevent running each time.
                }

                if (lives < 1) //If dead, pause all logic in the game.
                {
                    if (score > highScore) //Set new highscore
                    {
                        highScore = score;
                    }

                    MediaPlayer.Pause();

                    if (keyState.IsKeyDown(Keys.R)) //Restart game
                    {
                        RestartGame();

                        if (sound)
                        {
                            MediaPlayer.Resume();
                        }
                    }
                }
            }
            base.Update(gameTime);
        }
        /// <summary>
        /// Main method where we draw all our game objects
        /// </summary>
        /// <param name="gameTime"></param>
        protected override void Draw(GameTime gameTime)
        {
            GraphicsDevice.Clear(Color.CornflowerBlue);
            //Tells the game to start drawing
            spriteBatch.Begin();
            //Draw our background picture
            spriteBatch.Draw(map, new Vector2(0, 0), null, Color.White, 0, Vector2.Zero, 1, SpriteEffects.None, 0);
            //Draw sprite font
            spriteBatch.DrawString(text, $"Score: {score}\nLives: {lives}\n\nSound (V): On", new Vector2(0, 0), Color.White);

            foreach (GameObject go in gameObjects)//Loop for draw gameObjects
            {
                go.Draw(spriteBatch);  //Draw all spriteBatch

                DrawCollisionBox(go);  //Draw collision box
            }

            if (lives < 1) //If dead, call EndScreen draw method.
            {
                EndScreen();  //Call method EndScreen
            }

            StartScreen(); //Draws the start screen (to avoid instantly losing life upon start)
            //Tells the game to stop drawing
            spriteBatch.End();

            base.Draw(gameTime);
        }
        /// <summary>
        /// Method to make screensize for our game
        /// </summary>
        void GameScale()
        {
            graphics.PreferredBackBufferWidth = (int)(2400 * gameScale); //1200
            graphics.PreferredBackBufferHeight = (int)(1400 * gameScale); //700
            graphics.ApplyChanges();
            screenSize.X = graphics.PreferredBackBufferWidth;
            screenSize.Y = graphics.PreferredBackBufferHeight;
        }
        /// <summary>
        /// Method to draw a collision box
        /// </summary>
        /// <param name="gameObject"></param>
        private void DrawCollisionBox(GameObject gameObject)
        {
            Rectangle collisionBox = gameObject.GetCollisionBox();
            Rectangle topLine = new Rectangle(collisionBox.X, collisionBox.Y, collisionBox.Width, 1);
            Rectangle bottomLine = new Rectangle(collisionBox.X, collisionBox.Y + collisionBox.Height, collisionBox.Width, 1);
            Rectangle rightLine = new Rectangle(collisionBox.X + collisionBox.Width, collisionBox.Y, 1, collisionBox.Height);
            Rectangle leftLine = new Rectangle(collisionBox.X, collisionBox.Y, 1, collisionBox.Height);

            spriteBatch.Draw(collisionTexture, topLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, bottomLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, rightLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, leftLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
        }
        /// <summary>
        /// Method some we use when we want to add an object
        /// </summary>
        /// <param name="go"></param>
        public static void Instantiate(GameObject go)
        {
            newObjects.Add(go);
        }
        /// <summary>
        /// Method some we use when an object should be destroy
        /// </summary>
        /// <param name="go"></param>
        public static void Destroy(GameObject go)
        {
            deleteObjects.Add(go);
        }
        /// <summary>
        /// Method that is active when we start the game
        /// </summary>
        private void StartScreen()
        {
            if (!start)
            {
                //We write what we need to do to start game
                string stringTemp = "Press \"B\" to start";
                Vector2 stringSize = text.MeasureString(stringTemp);
                spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                    screenSize.Y / 2 - 70 - stringSize.Y), Color.White, 0, Vector2.Zero, 2f, 0, 0);
            }
        }
        /// <summary>
        /// Method that we use when end game
        /// </summary>
        private void EndScreen()
        {
            //We have info efter end of game
            string stringTemp = $"      GAME OVER\n You Achived a score \n               {score}" +
                $"\n with a Maximum score \n               {highScore}";
            Vector2 stringSize = text.MeasureString(stringTemp);
            spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                screenSize.Y / 2 - (int)(stringSize.Y * 1.5)), Color.White, 0, new Vector2(0, 0), 2f, 0, 0);
            stringTemp = "Press \"R\" to retry";
            stringSize = text.MeasureString(stringTemp);
            spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                screenSize.Y / 2 + (int)(stringSize.Y * 2.5)), Color.Yellow, 0, new Vector2(0, 0), 2f, 0, 0);
        }
        /// <summary>
        /// Method some we use to restart game when we lost
        /// </summary>
        private void RestartGame()
        {
            Initialize();
            LoadContent();
            start = true;
            lives = 3;
            score = 0;
            EnemySpeed();
        }
        /// <summary>
        /// Create speed for all enemies
        /// </summary>
        public static void EnemySpeed()
        {
            Random random = new Random();
            while (GameWorld.lives > 0) //When player is alive
            {
                if (GameWorld.score >= 0 && GameWorld.score <= 50)
                {
                    GameWorld.speed = random.Next(1, 4);
                    break;                    
                }
                if (GameWorld.score > 50 && GameWorld.score <= 100)
                {
                    GameWorld.speed = random.Next(3, 6);
                    break;                   
                }
                if (GameWorld.score > 100 && GameWorld.score <= 150)
                {
                    GameWorld.speed = random.Next(5, 8);
                    break;                    
                }
                if (GameWorld.score > 150)
                {
                    GameWorld.speed = 10;
                    break;
                }
            }            
        }
    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;

namespace Wizard_of_Wizards
{
    /// <summary>
    /// GameObject abstract class
    /// </summary>
    public abstract class GameObject
    {
        protected Texture2D sprite; //The active sprite used for drawing
        public Vector2 position; //Position data used for drawing the objects, inherited and used by Player & Enemy
        protected Color color;      //Make Color field 
        protected Vector2 origin;   //Make origin for gameObjects
        protected Vector2 velocity; //Make velocity field
        protected Vector2 offset;   //Create offset field for gameObjects
        protected float fps;        //Create field for frame per second(fps)
        protected Texture2D[] sprites; //Create array field
        protected float layer { get; set; } //Make field for layer
        protected float rotation;           //Create rotation for sprites
        protected Vector2 mousePos;         //Make field for mouse position
        protected Vector2 playerPos;        //Create field for player position
        protected float linearVelocity;     // Make field for linearVelocity-it's just a speed 


        //// <summary>
        /// Return a rectangle the size of the used image for an entity.
        /// GameScale is applied to adjust.
        /// </summary>
        /// <returns></returns> 
        public virtual Rectangle GetCollisionBox()
        {
            return new Rectangle(
                (int)(position.X + offset.X),
                (int)(position.Y + offset.Y),
                (int)(sprite.Width * (GameWorld.gameScale + GameWorld.scaleOffset)),
                (int)(sprite.Height * (GameWorld.gameScale + GameWorld.scaleOffset))
                );
        }
        /// <summary>
        /// Abstract LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public abstract void LoadContent(ContentManager content);

        /// <summary>
        /// Abstract Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public abstract void Update(GameTime gameTime);
        /// <summary>
        /// Master draw method. Called by everything.
        /// </summary>
        /// <param name="spriteBatch"></param>
        public void Draw(SpriteBatch spriteBatch)
        {
            spriteBatch.Draw(sprite, position, null, color, rotation, origin, 1f, SpriteEffects.None, layer);//new
        }
        /// <summary>
        /// Abstract OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public abstract void OnCollision(GameObject other);
        /// <summary>
        /// Checks if any collision boxes are overlapping, then calling OnColliion
        /// wherein the individual sub class can solve the collision. (Handled by Enemy & Wrench)
        /// </summary>
        /// <param name="other"></param>
        public void CheckCollision(GameObject other)
        {
            if (GetCollisionBox().Intersects(other.GetCollisionBox()))
            {
                OnCollision(other);
            }
        }
    }
}

using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;

namespace Wizard_of_Wizards
{
    /// <summary>
    /// Player class some is just one in this game
    /// </summary>
    class Player : GameObject
    {
        private Texture2D fire;   //Make field for fire texture

        private float Cooldown = 0f; //Cooldown field

        private Shield shield;   //Create field for shield object

        private SoundEffectInstance fireball;  //Make field for sound effect

        /// <summary>
        /// Empty player constructor
        /// </summary>
        public Player()
        {
            velocity = Vector2.Zero;
            color = Color.Red; //Set color red on the player
            linearVelocity = 3f;//Set speed for player
        }
        /// <summary>
        /// The Player constructor with position as parameter.
        /// </summary>
        /// <param name="playerPos"></param>
        public Player(Vector2 playerPos) // [-Mark Enemy 2.0-] An Attempt at getting the Players Position.
        {
            playerPos = this.position; //We need this position for our enemy
            //this.direction = direction;
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            sprite = content.Load<Texture2D>("TDWizard"); //Download player sprite

            Reset();

            fire = content.Load<Texture2D>("FireC");      //Download fire sprite

            fireball = content.Load<SoundEffect>("Fireball").CreateInstance(); //Download sound effect
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            HandleInput();
            HandleShootCooldown();
            ScreenLimits();

            playerPos = position; // Updates the player position which is attempted to be gained by enemy object.
        }
        public void HandleInput()
        {
            mousePos = new Vector2(Mouse.GetState().X, Mouse.GetState().Y); //Define mouse position as Vector2
            Vector2 direction = position - mousePos; //  Direction 
            rotation = (float)Math.Atan2(direction.Y, direction.X) - MathHelper.ToRadians(90); //Define rotation for player

            // direct movement
            if (Keyboard.GetState().IsKeyDown(Keys.W)) // if key W is down:
            {
                position.Y -= linearVelocity; // forward movement, which is done with "-" most likely due to some weird stuff with Rotations.
            }
            if (Keyboard.GetState().IsKeyDown(Keys.A)) // if key A is down:
            {
                position.X -= linearVelocity; // Left movement
            }
            if (Keyboard.GetState().IsKeyDown(Keys.S)) // if key S is down:
            {
                position.Y += linearVelocity; // backwards movement
            }
            if (Keyboard.GetState().IsKeyDown(Keys.D)) // if key D is down:
            {
                position.X += linearVelocity; // Right movement
            }

        }
        /// <summary>
        /// Make Shoot method where we instantiate fire
        /// </summary>
        private void Shoot()
        {
            GameWorld.Instantiate(new Fire(fire, new Vector2(position.X, position.Y),
                new Vector2(Mouse.GetState().X, Mouse.GetState().Y)));               //Add fire ability
            if (GameWorld.sound) // Add sound effect
            {
                fireball.Play();
            }
        }
        /// <summary>
        /// Limits the players movement to not leave the screen
        /// </summary>
        private void ScreenLimits()
        {
            if (position.Y - sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) < 0)
            {
                position.Y = sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.Y + sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.Y)
            {
                position.Y = GameWorld.screenSize.Y - sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.X - sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) < 0)
            {
                position.X = sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.X + sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.X)
            {
                position.X = GameWorld.screenSize.X - sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (GameWorld.lives <= 0 && other is Player)
            {
                GameWorld.Destroy(other);
            }
            if (other is MonsterEnemy || other is KnightEnemy || other is KnightEnemyRightSide)
            {
                Reset();
            }
        }
        /// <summary>
        /// Method for shoot cooldown
        /// </summary>
        private void HandleShootCooldown()
        {
            // Magic Attack
            if (Keyboard.GetState().IsKeyDown(Keys.Space) && (Cooldown <= 0))
            {
                Cooldown = 10;
                Shoot();
            }
            // Magic cooldown
            Cooldown--;
        }
        /// <summary>
        /// Method to reset player
        /// </summary>
        private void Reset()
        {
            // "this" (being the whole class) gets a designated position based on screen
            position = new Vector2(GameWorld.screenSize.X / 2 - sprite.Width / 2, GameWorld.screenSize.Y / 2 - sprite.Height / 2);
            // changes sprite origin from top left corner of sprite (0,0) to center of sprite
            origin = new Vector2(sprite.Height / 2, sprite.Width / 2);
            //Collider position
            offset = new Vector2(0 - sprite.Height / 2 + 10, 0 - sprite.Width / 2 + 10);
        }
        /// <summary>
        /// Method to add shield to player
        /// </summary>
        public void ApplyShield()
        {
            shield = new Shield(this, position);

            GameWorld.Instantiate(shield);
        }

    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;


namespace Wizard_of_Wizards
{
    enum SideOfSpawn //Make enum with 4 sides of screen
    {
        Up,
        Down,
        Left,
        Right
    }
    /// <summary>
    /// Create MonsterEnemy class
    /// </summary>
    class MonsterEnemy : GameObject
    {
        private Texture2D[] monsterEnemy = new Texture2D[10]; //Create field for monsterEnemy sprites
        private Random random = new Random();  //Random field
        private int index;
        private Player player = new Player();  //Make field Player object
        private KnightEnemy knightEnemy;     // Create field KnightEnemy object

        private SideOfSpawn sideOfSpawn;    // Make field for enum data type

        /// MonsterEnemy constructor with player some parameter
        /// </summary>
        /// <param name="player"></param>
        public MonsterEnemy(Player player)
        {
            offset = Vector2.Zero;
            color = Color.White;

            this.player = player;

            sideOfSpawn = (SideOfSpawn)random.Next(0, 3); //Sides chooses with random
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            for (int i = 0; i < 10; i++)
            {
                monsterEnemy[i] = content.Load<Texture2D>($"monster/monster{i + 1}"); //Download monster sprites
            }
            sprite = monsterEnemy[0];

            origin = new Vector2((sprite.Height) / 2, (sprite.Width) / 2); //Find origin for monsterEnemy
            offset.X = -sprite.Width / 2 + 9;   //Set offset for sprite
            offset.Y = -sprite.Height / 2 + 6;  //Set offset for sprite
            Create();
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            sideOfSpawn = (SideOfSpawn)random.Next(0, 3); // Update side of spawn of monsterEnemy

            if (index >= 10)       //When we used 10 different monster, it start first monster again
            {
                index = 0;
                Create();
            }
            if (GameWorld.lives == 0) //When player is dead
            {
                Remove();
                GameWorld.Destroy(knightEnemy);
            }
            EnemyMoveToPlayer(gameTime);
        }
        // <summary>
        /// Method move enemy into player
        /// </summary>
        /// <param name="gameTime"></param>
        private void EnemyMoveToPlayer(GameTime gameTime) //That method skal updates.
        {
            // The Direction of the Enemy.
            Vector2 direction = player.position - position;
            direction.Normalize(); // Normalize in Unity terms: Makes the Objects position Local instead of World.
            rotation = (float)Math.Atan2(direction.Y, direction.X) - MathHelper.ToRadians(90); // Tells the Enemy to face the Player, but only AFTER getting their position.

            // The Enemys Forward Movement into the direction they look at (which is the Player here)...
            position += direction * GameWorld.speed;
        }
        /// <summary>
        /// Method for create new enemy
        /// </summary>
        public void Create()
        {
            GameWorld.EnemySpeed();
            index = random.Next(0, monsterEnemy.Length);        // Make random enemy posiosion on the screen
            sprite = monsterEnemy[index];

            //
            SideOfEnemySpawn();


            //position.X = random.Next(sprite.Width, (int)GameWorld.screenSize.X - sprite.Width);
            //position.Y = -sprite.Height;
        }
        /// <summary>
        /// Method for destroy object
        /// </summary>
        private void Remove()
        {
            GameWorld.Destroy(this);
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (GameWorld.lives > 0) //It's happen when player is alive
            {
                if (other is Shield) //When this enemy colliders with shield
                {
                    GameWorld.Destroy(other);

                    Create();
                }

                if (other is Fire)   //When this enemy colliders with fire
                {
                    GameWorld.Destroy(other);

                    Create();
                }
                if (other is Player) //When this enemy colliders with player
                {
                    GameWorld.lives--;

                    //
                    SideOfEnemySpawn();

                    //position.X = random.Next(sprite.Width, (int)GameWorld.screenSize.X - sprite.Width);
                    //position.Y = -sprite.Height;
                }
            }
            else if (GameWorld.lives <= 0) //If player is dead
            {
                GameWorld.Destroy(other);
                GameWorld.Destroy(this);
            }
        }
        private void SideOfEnemySpawn()
        {

            switch (sideOfSpawn)       // Create switch statement for left and right side
            {
                //Enemy spawn op from
                case SideOfSpawn.Up:
                    position.X = random.Next(sprite.Width, (int)GameWorld.screenSize.X - sprite.Width);
                    position.Y = -sprite.Height;
                    break;
                //Enemy spawn down from
                case SideOfSpawn.Down:
                    position.X = random.Next(sprite.Width, (int)GameWorld.screenSize.X - sprite.Width);
                    position.Y = (int)GameWorld.screenSize.Y + sprite.Height;
                    break;
                //Enemy spawn from left side
                case SideOfSpawn.Left:
                    position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
                    position.X = -sprite.Width;
                    break;
                //Enemy spawn from right side
                case SideOfSpawn.Right:
                    position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
                    position.X = (int)GameWorld.screenSize.X + sprite.Width;
                    break;
            }
        }

    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;


namespace Wizard_of_Wizards
{

    /// <summary>
    /// Create KnightEnemy class
    /// </summary>
    class KnightEnemy : GameObject
    {
        private Random random;     //Random field
        private Texture2D[] knightSprites = new Texture2D[5]; //Sprites array
        private float knightrunFps;                  //Amount frequence per second
        private int index;
        private Player player = new Player(); // Create Player object class

        /// KnightEnemy constructor with player some parameter
        /// </summary>
        /// <param name="player"></param>
        public KnightEnemy(Player player)
        {
            random = new Random();
            offset = Vector2.Zero;
            color = Color.White;
            this.player = player;
            knightrunFps = 0;
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            for (int i = 0; i < 5; i++) // Loop for download every sprite
            {
                knightSprites[i] = content.Load<Texture2D>($"EnemyAnimation/EnemyFrame{i + 1}");//Download every sprite
            }

            sprite = knightSprites[0];

            origin = new Vector2(sprite.Height / 2, sprite.Width / 2);//Find origin for sprite
            offset.X = -sprite.Width / 2 + 8;             // Set offset X for sprite
            offset.Y = -sprite.Height / 2 + 8;            // Set offset Y for sprite

            CreateKnightSprites();
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            EnemyMoveToPlayer(gameTime); // Update move enemy into player

            knightrunFps += 0.09f; // 2 frames pr image

            if (knightrunFps >= 4)
            {
                knightrunFps = 0;
                index = 0;
            }
            sprite = knightSprites[(int)knightrunFps];
        }
        /// <summary>
        /// Create knightSprites
        /// </summary>
        public void CreateKnightSprites()
        {
            GameWorld.EnemySpeed(); //Set enemies speed
            index = random.Next(0, knightSprites.Length);
            sprite = knightSprites[index];
            position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
            position.X = -sprite.Width;
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (GameWorld.lives > 0)  //When Player is alive
            {
                if (other is Shield)  //When this enemy colliders with shield
                {
                    GameWorld.Destroy(other);

                    CreateKnightSprites();
                }
                if (other is Fire)    //When this enemy colliders with fire
                {
                    GameWorld.Destroy(other);

                    CreateKnightSprites();
                }
                if (other is Player)  //When enemy colliders with player
                {
                    GameWorld.lives--;

                    position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
                    position.X = -sprite.Width;
                }
            }
            else if (GameWorld.lives <= 0) // If dead destroy
            {
                GameWorld.Destroy(other);
                GameWorld.Destroy(this);
            }
        }

        /// <summary>
        /// Method move enemy into player
        /// </summary>
        /// <param name="gameTime"></param>
        private void EnemyMoveToPlayer(GameTime gameTime)
        {
            // A Reaffirmation of the Enemys positions.
            //this.position = new Vector2(position.X, position.Y);

            // The Direction of the Enemy.
            Vector2 direction = player.position - position;
            direction.Normalize(); // Normalize in Unity terms: Makes the Objects position Local instead of World.
            rotation = (float)Math.Atan2(direction.Y, direction.X) - MathHelper.ToRadians(90); // Tells the Enemy to face the Player, but only AFTER getting their position.

            // The Enemys Forward Movement into the direction they look at (which is the Player here)...
            position += direction * GameWorld.speed;
        }

    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;

namespace Wizard_of_Wizards
{
    /// <summary>
    /// Knight enemy class
    /// </summary>
    class KnightEnemyRightSide : GameObject
    {
        private Random random;  //Random field
        private Texture2D[] knightSpritesRight = new Texture2D[5]; //Sprites array
        private float knightrunFps = 0;      //Amount frequence per second
        private int index;
        private Player player = new Player(); // Create Player object class

        /// <summary>
        /// KnightEnemy constructor with player some parameter
        /// </summary>
        /// <param name="player"></param>
        public KnightEnemyRightSide(Player player)
        {
            random = new Random();
            offset = Vector2.Zero;
            color = Color.White;
            this.player = player;
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            for (int i = 0; i < 5; i++) // Loop for download every sprite
            {
                knightSpritesRight[i] = content.Load<Texture2D>($"EnemyAnimation/EnemyFrame{i + 1}");//Download every sprite
            }

            sprite = knightSpritesRight[0];

            origin = new Vector2(sprite.Height / 2, sprite.Width / 2);//Find origin for sprite
            offset.X = -sprite.Width / 2 + 8;             // Set offset X for sprite
            offset.Y = -sprite.Height / 2 + 8;            // Set offset Y for sprite

            CreateKnightSprites();
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            EnemyMoveToPlayer(gameTime); // Update move enemy into player

            knightrunFps += 0.09f; // 2 frames pr image

            if (knightrunFps >= 4)
            {
                knightrunFps = 0;
                index = 0;
            }
            sprite = knightSpritesRight[(int)knightrunFps];
        }
        /// <summary>
        /// Create knightSprites
        /// </summary>
        public void CreateKnightSprites()
        {
            GameWorld.EnemySpeed(); //Create speed for this enemy
            index = random.Next(0, knightSpritesRight.Length);
            sprite = knightSpritesRight[index];
            position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
            position.X = (int)GameWorld.screenSize.X + sprite.Width;
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (GameWorld.lives > 0) //When Player is alive
            {
                if (other is Shield) //When this enemy colliders with shield
                {
                    GameWorld.Destroy(other);

                    CreateKnightSprites();
                }
                if (other is Fire)  //When this enemy colliders with fire
                {
                    GameWorld.Destroy(other);

                    CreateKnightSprites();
                }
                if (other is Player) //When this enemy colliders with player
                {
                    GameWorld.lives--;

                    position.Y = random.Next(sprite.Height, (int)GameWorld.screenSize.Y - sprite.Height);
                    position.X = (int)GameWorld.screenSize.X + sprite.Width;
                }
            }
            else if (GameWorld.lives <= 0) // If dead destroy
            {
                GameWorld.Destroy(other);
                GameWorld.Destroy(this);
            }
        }

        /// <summary>
        /// Method move enemy into player
        /// </summary>
        /// <param name="gameTime"></param>
        private void EnemyMoveToPlayer(GameTime gameTime)
        {
            // A Reaffirmation of the Enemys positions.
            //this.position = new Vector2(position.X, position.Y);

            // The Direction of the Enemy.
            Vector2 direction = player.position - position;
            direction.Normalize(); // Normalize in Unity terms: Makes the Objects position Local instead of World.
            rotation = (float)Math.Atan2(direction.Y, direction.X) - MathHelper.ToRadians(90); // Tells the Enemy to face the Player, but only AFTER getting their position.

            // The Enemys Forward Movement into the direction they look at (which is the Player here)...
            position += direction * GameWorld.speed;
        }
    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;


namespace Wizard_of_Wizards
{
    /// <summary>
    /// Fire class
    /// </summary>
    class Fire : GameObject
    {
        private ExplosionEffect explode; //Create field of object ExplosionEffect class
        private Crate crate;             //Make field of object Crate
        private SoundEffectInstance exploded; // Add field of SoundEffectInstance class

        public Fire(Texture2D sprite, Vector2 position, Vector2 mousePos)
        {
            linearVelocity = 6f;
            this.sprite = sprite;
            this.position = position;
            color = Color.White;

            this.mousePos = new Vector2(Mouse.GetState().X, Mouse.GetState().Y); //define mouse position as Vector2
            Vector2 dPos = position - mousePos; // "dPos = Direction Position"
            rotation = (float)Math.Atan2(dPos.Y, dPos.X) - MathHelper.ToRadians(90);
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            origin = new Vector2(sprite.Height / 2, sprite.Width / 2); //Create origin for fire sprite

            offset = new Vector2(0 - sprite.Height / 2 + 4, 0 - sprite.Width / 2 + 4); //Collider position, 4 fordi størrelse af rectangle er halvdelen af sprite størrelse(16), og skal rykkes 

            exploded = content.Load<SoundEffect>("Explode").CreateInstance(); //Dowload explosion sound
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (other is MonsterEnemy || other is KnightEnemy || other is KnightEnemyRightSide)
            {
                GameWorld.score++;                               // Add point when we score

                crate = new Crate(position);                     // Call crate constructor
                GameWorld.Instantiate(crate);                     // Add crate effect 

                explode = new ExplosionEffect(position);          // Call explosion constructor
                GameWorld.Instantiate(explode);                    // Add explosion effect

                if (GameWorld.sound)
                {
                    exploded.Play();                 // Play effect if sound is on
                }
            }
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            Vector2 directionNS = new Vector2((float)Math.Cos(MathHelper.ToRadians(90) - rotation), -(float)Math.Sin(MathHelper.ToRadians(90) - rotation));

            position += directionNS * linearVelocity;
            //We will destroy fire sprite when it is out of the screen
            if (position.Y - sprite.Height *
                (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.Y)//Down side of the screen
            {
                GameWorld.Destroy(this);
            }
            if (position.Y < -sprite.Height * (GameWorld.gameScale + GameWorld.scaleOffset))//Up side of the screen
            {
                GameWorld.Destroy(this);
            }
            if (position.X - sprite.Width * (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.X)//Right side of the screen
            {
                GameWorld.Destroy(this);
            }
            if (position.X < -sprite.Width * (GameWorld.gameScale + GameWorld.scaleOffset))//Left side of the screen
            {
                GameWorld.Destroy(this);
            }

        }
    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;


namespace Wizard_of_Wizards
{
    /// <summary>
    /// Make enum for life and shield
    /// </summary>
    enum SupplyType
    {
        Life,
        Shield
    }
    /// <summary>
    /// Make Crate class some inherits from Gameobjects class
    /// </summary>
    class Crate : GameObject
    {
        private SupplyType supplyType; // Make a field of SupplyType enum

        private Random rnd = new Random(); //Field a Random
        /// <summary>
        /// Make Crate connstructor
        /// </summary>
        /// <param name="position"></param>
        public Crate(Vector2 position)
        {
            this.position = position;
            offset = Vector2.Zero;
            color = Color.White;
            supplyType = (SupplyType)rnd.Next(0, 3); //Create 25% chance to find life or shield in a crate
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            sprite = content.Load<Texture2D>("crate"); //Download crate sprite

            origin = new Vector2(sprite.Height / 2, sprite.Width / 2); //Find origin for crate sprite
            offset.X = sprite.Width / 2 - 27;                          //Set offset X for sprite
            offset.Y = sprite.Height / 2 - 28;                         //Set offset Y for sprite
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other)
        {
            if (other is Player) //When crate collider player we can find life or shield
            {
                switch (supplyType)       // Create switch statement for life and shield
                {
                    case SupplyType.Life:
                        GameWorld.lives++;
                        break;
                    case SupplyType.Shield:
                        (other as Player).ApplyShield();
                        break;
                }
                GameWorld.Destroy(this);
            }
            if (GameWorld.lives <= 0 && other is Crate) //Destroy crate when player is dead 
            {
                GameWorld.Destroy(other);
            }
        }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            ScreenLimits();
        }
        /// <summary>
        /// Make screen limits for crate - they should spawn indside
        /// </summary>
        private void ScreenLimits()
        {
            if (position.Y - sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) < 0)
            {
                position.Y = sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.Y + sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.Y)
            {
                position.Y = GameWorld.screenSize.Y - sprite.Height / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.X - sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) < 0)
            {
                position.X = sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
            if (position.X + sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset) > GameWorld.screenSize.X)
            {
                position.X = GameWorld.screenSize.X - sprite.Width / 2 * (GameWorld.gameScale + GameWorld.scaleOffset);
            }
        }
    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;


namespace Wizard_of_Wizards
{
    /// <summary>
    /// ExplosionEffect class where we make explosion
    /// </summary>
    class ExplosionEffect : GameObject
    {
        private static Texture2D[] explosion = new Texture2D[16]; //array with 8 spaces for 8 difrent explosion frames to make animation
        private float explosionFps = 0;

        /// <summary>
        /// Sets the location of the explosion effect
        /// </summary>
        /// <param name="position"></param>
        public ExplosionEffect(Vector2 position)
        {
            this.position = new Vector2(position.X - 40, position.Y - 40);
            offset = Vector2.Zero;
            color = Color.White;
        }
        /// <summary>
        /// Override LoadContent method where it plays the explosion animation with a for loop
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            for (int i = 0; i < 16; i++)     //Create loaad for 16 explosion sprites
            {
                explosion[i] = content.Load<Texture2D>($"explosion/explosion{i + 1}"); //Download explosion sprites
            }
            sprite = explosion[0];  //Start from first sprite 

            origin = new Vector2(sprite.Height / 100, sprite.Width / 100);//Set origin for sprite
            offset.X = sprite.Width / 2 - 21;   //Make offset for X
            offset.Y = sprite.Height / 2 - 15;  //Make offset for Y
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other) { }

        /// <summary>
        /// Override Update method where we set explosion fps and destroys it when it is done with its animation
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            explosionFps += 0.25f; // 4 frames pr explosion image
            if (explosionFps > 15)
            {
                GameWorld.Destroy(this);
            }
            sprite = explosion[(int)explosionFps];
        }

    }
}

using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;


namespace Wizard_of_Wizards
{
    /// <summary>
    /// Class Shield
    /// </summary>
    class Shield : GameObject
    {
        private Player player;   //Create player object

        /// <summary>
        /// Create Shield constructor
        /// </summary>
        /// <param name="player"></param>
        /// <param name="position"></param>
        public Shield(Player player, Vector2 position)
        {
            this.position = position;
            color = Color.White;
            this.player = player;
        }
        /// <summary>
        /// Override LoadeContent method
        /// </summary>
        /// <param name="content"></param>
        public override void LoadContent(ContentManager content)
        {
            sprite = content.Load<Texture2D>("shield"); //Dowload shield sprite

            origin = new Vector2(sprite.Height / 2, sprite.Width / 2); // Find origin for shield sprite

            offset = new Vector2(0 - sprite.Height / 2 + 18, 0 - sprite.Width / 2 + 18); //Collider position, 4 fordi størrelse af rectangle er halvdelen af sprite størrelse(16), og skal rykkes
        }
        /// <summary>
        /// Override OnCollision method
        /// </summary>
        /// <param name="other"></param>
        public override void OnCollision(GameObject other) { }
        /// <summary>
        /// Override Update method
        /// </summary>
        /// <param name="gameTime"></param>
        public override void Update(GameTime gameTime)
        {
            this.position = player.position; //Set shield position in player position
        }
    }
}

